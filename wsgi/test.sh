clear

WSGI_DIR=$(dirname $0)

start_server() {
  echo "Starting server..."
  (uwsgi --ini $WSGI_DIR/wsgi.ini &>$WSGI_DIR/wsgi.log &)
  read PID < <(pgrep -f "uwsgi --ini $WSGI_DIR/wsgi.ini")
  echo "Server started with PID $PID"
}
restart_server() {
  echo "Restarting server..."
  kill -9 $PID &>/dev/null
  sleep 3
  (uwsgi --ini $WSGI_DIR/wsgi.ini &>$WSGI_DIR/wsgi.log &)
  read PID < <(pgrep -f "uwsgi --ini $WSGI_DIR/wsgi.ini")
  echo "Server started with PID $PID"
}
stop_server() {
  echo "Stopping server..."
  kill -9 $PID &>/dev/null
  sleep 3
  echo "Server stopped"
}

start_server
trap stop_server EXIT
while inotifywait -q -r -e modify --exclude '__pycache__' src; do
  restart_server
done
