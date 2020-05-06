class AudienciaModel:

    def __init__(self, aud_prc_id=None,
                 aud_plp_id=None,
                 aud_usr_id=None,
                 aud_tipo=None,
                 aud_data=None,
                 aud_status=None,
                 aud_obs=None):
        self.aud_prc_id = aud_prc_id
        self.aud_plp_id = aud_plp_id
        self.aud_usr_id = aud_usr_id
        self.aud_data = aud_data
        self.aud_tipo = aud_tipo
        self.aud_status = aud_status
        self.aud_obs = aud_obs