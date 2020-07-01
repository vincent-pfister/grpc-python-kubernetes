# grpc-python-kubernetes
This is a python3 gRPC service/client for testing gRPC services inside a Kubernetes cluster using k3d + traefik. 
It consist of a single service that responds with a UUID that is randomly generated at creation. The unique UUID response is useful for indicating that the responses are coming back from different instances of the service.

### Generate gRPC Code
```
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. getid.proto
```

### Build Docker Image
```
docker build -t vprp/grpc-python-kubernetes .
docker push vprp/grpc-python-kubernetes
```

### TLS certificate

create the certificate:
```shell script
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=gpd.vega.local.raisepartner.com"
```
See [TLS Cert Instructions](https://github.com/kubernetes/contrib/tree/master/ingress/controllers/nginx/examples/tls)

After you have created the SSL certificate and created the Kubernetes secret, you must create a .pem file for the client to use.
```
cat tls.crt tls.key > tls.pem
```

### Run without TLS in docker

Run the server:
```
docker run -it --rm -p 0.0.0.0:50051:50051 --name grpc-server vprp/grpc-python-kubernetes
```

Run the client without TLS, server in docker (use the host IP):
```shell script
python client.py 192.168.21.53:50051
```

Run the client with TLS, which fails:
```
$ python client.py vega.local.raisepartner.com:50051 --cert tls.pem
E0701 01:13:01.524271575  234075 ssl_transport_security.cc:1395] Handshake failed with fatal error SSL_ERROR_SSL: error:100000f7:SSL routines:OPENSSL_internal:WRONG_VERSION_NUMBER.
Traceback (most recent call last):
  File "client.py", line 45, in <module>
    run(server_, options_)
  File "client.py", line 37, in run
    response = stub.RequestID(getid_pb2.IDRequest())
  File "/home/vincent/.local/share/virtualenvs/grpc-python-kubernetes-ujl0uD3D/lib/python3.8/site-packages/grpc/_channel.py", line 826, in __call__
    return _end_unary_response_blocking(state, call, False, None)
  File "/home/vincent/.local/share/virtualenvs/grpc-python-kubernetes-ujl0uD3D/lib/python3.8/site-packages/grpc/_channel.py", line 729, in _end_unary_response_blocking
    raise _InactiveRpcError(state)
grpc._channel._InactiveRpcError: <_InactiveRpcError of RPC that terminated with:
        status = StatusCode.UNAVAILABLE
        details = "failed to connect to all addresses"
        debug_error_string = "{"created":"@1593558781.524324819","description":"Failed to pick subchannel","file":"src/core/ext/filters/client_channel/client_channel.cc","file_line":3948,"referenced_errors":[{"created":"@1593558781.524323735","description":"failed to connect to all addresses","file":"src/core/ext/filters/client_channel/lb_policy/pick_first/pick_first.cc","file_line":394,"grpc_status":14}]}"
```

### Run with TLS in k3d + traefik

Create the TLS secret with the self-signed certificate
```shell script
kubectl create secret tls --key tls.key --cert tls.crt gpd-secret
```

**Important:**
You will need to change the host in the *IngressRoute* with a domain that points to your ingress controller.

```
kubectl apply -f gpd-self.yaml
```

Run the client with TLS:
```shell script
python client.py gpd.vega.local.raisepartner.com --cert tls.pem
```
