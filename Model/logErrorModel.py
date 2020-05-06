from Model.toolsModel import *
import logging


class LogErrorModel:
    def __init__(self, platform_name, state):
        pass
        # self.state = state
        # self.platform_name = platform_name
        # self.directory = os.path.abspath('../Logs/' + self.platform_name + '/' + self.state + '/')
        # Tools.new_path(self.directory)
        # self.filename = self.directory + '/' + self.state + '_logging_exec.log'
        # self.logger = logging.getLogger(self.filename)
        # logging.basicConfig(filename=self.filename, filemode='a+', format='%(asctime)s - %(levelname)s - %(message)s',
        #                     datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

    def insert_title(self, n_proc):
        return
        # self.logger.info('{}\n{}'.format('-' * 48, '#' * 76).upper())
        # self.logger.info('Processo: {}'.format(n_proc).upper())

    def insert_log(self, log):
        return
        # self.logger.error(log.upper())

    def insert_info(self, info):
        return
        # self.logger.info(info.upper())


class LogErrorModelMutlThread:
    def __init__(self, platform_name=None, state=None, num_thread=None,grau='Default'):
        pass
        # self.state = state
        # self.grau=grau
        # self.platform_name = platform_name
        # self.num_tread = "" if num_thread is None else num_thread
        # self.logger = logging.getLogger('tr{}'.format(num_thread))
        # self.logger.setLevel(logging.INFO)
        # self.Handler = None
        #
        # if self.state is not None:
        #     self.set_Handler(self.state)

    def insert_title(self, n_proc):
        return
        # self.logger.info('{}\n{}'.format('-' * 48, '#' * 76).upper())
        # self.logger.info('Processo: {}'.format(n_proc).upper())

    def insert_log(self, log):
        return
        # self.logger.error(log.upper())

    def insert_info(self, info):
        return
        # self.logger.info(info.upper())

    def set_Handler(self, state):
        return
        # directory = os.path.abspath('../../Logs/' + self.platform_name + '/' + state + '/'+str(self.grau)+"GRAU")
        # Tools.new_path(directory)
        # self.logger = logging.getLogger('tr{}_{}_{}'.format(self.num_tread, state,self.grau))
        # self.logger.setLevel(logging.INFO)
        #
        # if self.Handler is not None:
        #     self.logger.handlers.clear()
        #
        # self.Handler = logging.FileHandler(directory + '/' + state + '_logging_exec_{}.log'.format(self.num_tread),
        #                                    mode='a+')
        # self.Handler.setFormatter(
        #     logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'))
        # self.logger.addHandler(self.Handler)
