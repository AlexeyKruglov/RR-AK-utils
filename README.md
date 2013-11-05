Arduino-proxy
=============

Proxy server to connect to Arduino board and prevent resets on reconnections.

Normally, Arduino's DTR line is connected to its RESET pin through capacitor, so Arduino restarts every time Linux PC connects to its virtual serial port. Linux serial port driver switches DTR line on every connect/disconnect, and AFAIK this cannot be changed by users. This proxy server connects to Arduino board, keeps the connection alive and relays messages received through a UNIX socket.
