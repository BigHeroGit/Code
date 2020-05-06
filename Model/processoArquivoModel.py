class ProcessoArquivoModel:

    def __init__(self, pra_prc_id=None,
                 pra_acp_id=None,
                 pra_url=None,
                 pra_nome=None,
                 pra_descricao=None,
                 pra_erro=False):
        self.pra_prc_id = pra_prc_id
        self.pra_acp_id = pra_acp_id
        self.pra_url = pra_url
        self.pra_nome = pra_nome
        self.pra_descricao = pra_descricao
        self.pra_erro = pra_erro
