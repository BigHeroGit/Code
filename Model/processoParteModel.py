class ProcessoParteModel():
    def __init__(self, ppt_id=None,
                 ppt_prc_id=None,
                 ppt_prt_id=None,
                 ppt_tipo=None,
                 ppt_polo=None,
                 ppt_plp_id=None):
        self.ppt_id = ppt_id
        self.ppt_prc_id = ppt_prc_id
        self.ppt_plp_id = ppt_plp_id
        self.ppt_prt_id = ppt_prt_id
        self.ppt_tipo = ppt_tipo
        self.ppt_polo = ppt_polo