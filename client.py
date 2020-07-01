from __future__ import print_function

import signal
import sys
from optparse import OptionParser

import grpc

import getid_pb2
import getid_pb2_grpc


def parse_options(argv):
    parser = OptionParser("usage: %prog [options] <server>")
    parser.add_option("-c", "--cert", help="server certificate", dest="cert")
    parser.add_option("-s", "--secure", action="store_true", help="use a secure channel, ignored if --cert is given",
                      dest="secure")
    parser.add_option("-n", default=10, type="int", help="number of request, 0 for infinite", dest="num")
    options, args = parser.parse_args(args=argv[1:])
    if len(args) != 1:
        parser.error("missing <server>")
    return args[0], options


def sigint_handler(signum, frame):
    exit()


signal.signal(signal.SIGINT, sigint_handler)


def run(server, options):
    if options.cert is not None:
        creds = grpc.ssl_channel_credentials(open(options.cert, 'rb').read())
        channel = grpc.secure_channel(server, creds)
    elif options.secure:
        creds = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(server, creds)
    else:
        channel = grpc.insecure_channel(server)
    stub = getid_pb2_grpc.InformationStub(channel)
    response = stub.RequestID(getid_pb2.IDRequest())
    print(response.message)


if __name__ == '__main__':
    server_, options_ = parse_options(sys.argv)
    count = 0
    while options_.num == 0 or count < options_.num:
        run(server_, options_)
        count += 1
