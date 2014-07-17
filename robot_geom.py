# Cartesian to motor coordinate converter base class

from math import *

# Coordinate naming convention:
#  x,y,z  are  Cartesian coordinates
#  X,Y,Z  are  robot coordinates

class RobotGeometryBase:
  def c2r(self, x,y,z):  # Cartesian to motor coordinate converter
    raise ValueError("RobotGeometryBase r2c() method should be inherited")

class RobotGeometryAK(RobotGeometryBase):
  ## Very approximate yet:
  ##R1=160      # +-10, mm
  ##R2=87       # +-10, mm
  ##Xperp=60.0  # +-5, mm
  #Yperp=272.2*pi/2
  ##phi1k=269   # +-5, mm
  ##phi2k=115   # +-5, mm
  #R1=160.8311
  #R2=76.435
  #Xperp=90.8311
  #phi1k=272.2
  #phi2k=115.573

  R1              = 158.162         # +/- 1.408        (0.8902%)
  #Xperp_probe           = 86.0537  #        +/- 2.751        (3.196%)
  #R2_probe              = 72.9029  #        +/- 1.995        (2.737%)
  R2              = 94.9426         # +/- 3.049        (3.212%)
  Xperp           = 65.7656         # +/- 1.868        (2.841%)
  phi1k           = 270.429         # +/- 2.051        (0.7584%)
  phi2k           = 108.933         # +/- 3.728        (3.422%)
  Yperp           = -180.322        # +/- 5.797        (3.215%)
  xx0             = -235.9          # +/- 2.102        (0.8912%)
  yy0             = 26.8296         # +/- 2.627        (9.79%)

  # additive const: z shift at x=y=0
  #z0  = -6.11831  # mm(Z)
  #z0  = -5.44919
  z0=0

  def __init__(self):
    pass

  def table_Z0(self, X,Y):
    ## Fit results by plot-probe.gp with probe3.dat:
    ## tilt of the upper disc
    #sx  = 0.543657  # mm(Z)
    #sy  = 0.836719  # mm(Z)
    ## tilt of the lower disc (table)
    #px  = 0.00931464  # 1
    #py  = 0.00325368  # 1
    ## table warp (mine is warped)
    #pxx = -2.74275e-05  # 1/mm(xy)
    #pxy = -4.42087e-06  # 1/mm(xy)
    ## table wheel excentricity sine and cosine components
    #ws  = 0.000251083  # 1
    #wc  = 0.000394223  # 1
    ## position of the table support wire
    #p2a = 0.812886  # rad
    ## table wheel turn period along Y
    #wp  = 86.8356  # mm(Y)

    sx              = 0.942001
    sy              = 0.961247
    px              = 0.00430328
    py              = 0.00109359
    pxx             = -2.71321e-05
    pxy             = 3.09371e-06
    ws              = 0 * 0.000302164
    wc              = 0 * 0.000452948
    p2a             = 0.875118
    wp              = 86.7701

    # No xx0, yy0, Yperp shift here:
    phi1=(Y           )/self.phi1k
    phi2=(X-self.Xperp)/self.phi2k-pi/2
    x=self.R1*cos(phi1)+self.R2*cos(phi1+phi2)
    y=self.R1*sin(phi1)+self.R2*sin(phi1+phi2)

    p2skew = sx*cos(phi2)+sy*sin(phi2)
    plane = px*x+py*y
    plane2 = cos(p2a)*x+sin(p2a)*y
    warp = pxx*(x**2 - y**2) + 2*pxy*x*y  # zero average curvature
    Z0 = p2skew + plane + warp + (ws*sin(2*pi*Y/wp) + wc*cos(2*pi*Y/wp)) * plane2 + self.z0
    return Z0

  def r2c_approx(self, X,Y,Z):
    phi1=(Y-self.Yperp)/self.phi1k  #+pi/2
    phi2=(X-self.Xperp)/self.phi2k-pi/2

    x=self.R1*cos(phi1) + self.R2*cos(phi1+phi2) + self.xx0
    y=self.R1*sin(phi1) + self.R2*sin(phi1+phi2) + self.yy0
    z=Z

    return (x,y,z)

  def c2r_approx(self, x,y,z):
    Z=z
    x -= self.xx0
    y -= self.yy0
    r2=x**2+y**2
    r=sqrt(r2)
    phi=atan2(y,x)
    psi1= acos( (self.R1**2+r2-self.R2**2)/(2*self.R1*r))
    psi2=-acos(-(self.R1**2+self.R2**2-r2)/(2*self.R2*self.R1))
    X=(psi2+pi/2)*self.phi2k + self.Xperp
    # Y=(phi+psi1-pi/2)*self.phi1k + self.Yperp
    Y=(phi+psi1)*self.phi1k + self.Yperp
    return (X,Y,Z)

  def c2r(self, x,y,z):
    X,Y,Z1=self.c2r_approx(x,y,z)
    #print "c2r: X=%f Y=%f" % (X,Y)
    return (X, Y, Z1+self.table_Z0(X,Y))

  def r2c(self, X,Y,Z):
    x,y,z=self.r2c_approx(X, Y, Z - self.table_Z0(X,Y))
    return (x,y,z)
