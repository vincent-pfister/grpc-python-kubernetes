import logging
import uuid
from concurrent import futures

import grpc

import getid_pb2
import getid_pb2_grpc

id_ = uuid.uuid4()
logger = logging.getLogger(__name__)


class Information(getid_pb2_grpc.InformationServicer):
    def RequestID(self, request, context):
        logger.info("RequestId")
        return getid_pb2.IDReply(message='ID: %s' % id_)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    getid_pb2_grpc.add_InformationServicer_to_server(Information(), server)
    server.add_insecure_port('[::]:50051')
    logger.info("starting server")
    server.start()
    server.wait_for_termination()
    logger.info("server stopped")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    serve()
