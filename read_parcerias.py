from Repository.ParceriaRepository import ParceriaRepository


def get_parcerias():
    parceria_repository = ParceriaRepository()
    parcerias = parceria_repository.getAll()
    return parcerias

def get_ofertas():
    parceria_repository = ParceriaRepository()
    parcerias = parceria_repository.getAll()
    ofertas = [parc for parc in parcerias if parc.oferta and parc.inicio is not None]
    return ofertas
