#!/bin/bash
# Start HydraDB node in background
ROOT=/tmp/sgk-local
HYDRADB_DIR=/home/shrinjali/Desktop/Blackout/hydradb

# Kill any existing node
if [ -f "$ROOT/node.pid" ]; then
    kill "$(cat $ROOT/node.pid)" 2>/dev/null || true
    rm -f "$ROOT/node.pid"
fi

# Clean and recreate data dir
rm -rf -- "$ROOT/store" "$ROOT/cache"
mkdir -p "$ROOT/store" "$ROOT/cache"
printf '%s\n' 'local-dev-auth-token-32-characters-long' > "$ROOT/auth-token"

# Environment
export CLOUD_PROVIDER=local
export LOCAL_PATH="$ROOT/store"
export GRAPH_NAMESPACE=local
export GRAPH_ID=default
export GRAPH_CELL_ID=cell-0
export GRAPH_CELLS=cell-0
export GRAPH_DATA_PATH=data
export GRAPH_ALLOW_PLAINTEXT=true
export GRAPH_AUTH_TOKEN_FILE="$ROOT/auth-token"
export GRAPH_DATA_CACHE_BYTES=67108864
export GRAPH_DATA_CACHE_DIR="$ROOT/cache"
export GRAPH_NODE_ID=node-0
export GRAPH_BOLT_ADDR=127.0.0.1:7687
export GRAPH_ADVERTISED_BOLT_ADDR=127.0.0.1:7687
export GRAPH_BOLT_NODE_ADDRESSES=node-0=127.0.0.1:7687
export GRAPH_HTTP_ADDR=127.0.0.1:8443
export GRAPH_ADMIN_ADDR=127.0.0.1:9090
export RUST_MIN_STACK=33554432
export RUST_LOG=info
export BINDGEN_EXTRA_CLANG_ARGS="-I/usr/lib/gcc/x86_64-linux-gnu/13/include"

cd "$HYDRADB_DIR"
nohup target/debug/graph-node > "$ROOT/node.log" 2>&1 &
echo $! > "$ROOT/node.pid"
echo "HydraDB started with PID $(cat $ROOT/node.pid)"

# Wait for readyz
echo "Waiting for HydraDB to be ready..."
for i in $(seq 1 30); do
    if curl -fsS http://127.0.0.1:9090/readyz >/dev/null 2>&1; then
        echo "HydraDB is READY on port 7687 (Bolt), 8443 (HTTP), 9090 (Admin)"
        exit 0
    fi
    sleep 1
done

echo "HydraDB failed to start. Check $ROOT/node.log"
tail -20 "$ROOT/node.log"
exit 1
