class processoModel:

    def __init__(self, prc_sequencial=None,
                 prc_numero=None,
                 prc_carteira=None,
                 prc_estado=None,
                 prc_parte_ativa=None,
                 prc_parte_passiva=None,
                 prc_objeto1=None,
                 prc_objeto2=None,
                 prc_objeto3=None,
                 prc_objeto4=None,
                 prc_data_cadastro=None,
                 prc_area=None,
                 prc_apto_pgto=None,
                 prc_penhora=None,
                 prc_responsavel=None
                 ):
        self.prc_sequencial = prc_sequencial
        self.prc_numero = prc_numero
        self.prc_estado = prc_estado
        self.prc_carteira = prc_carteira
        self.prc_parte_ativa = prc_parte_ativa
        self.prc_parte_passiva = prc_parte_passiva
        self.prc_objeto1 = prc_objeto1
        self.prc_objeto2 = prc_objeto2
        self.prc_objeto3 = prc_objeto3
        self.prc_objeto4 = prc_objeto4
        self.prc_data_cadastro = prc_data_cadastro
        self.prc_area=prc_area
        self.prc_apto_pgto=prc_apto_pgto
        self.prc_penhora=prc_penhora
        self.prc_responsavel=prc_responsavel
