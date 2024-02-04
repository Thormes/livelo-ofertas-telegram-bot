from Repository.ParceriaRepository import ParceriaRepository


def get_parcerias():
    parceria_repository = ParceriaRepository()
    parcerias_salvas = parceria_repository.getAll()
    return parcerias_salvas


def get_ofertas():
    parceria_repository = ParceriaRepository()
    parcerias_salvas = parceria_repository.getAll()
    ofertas = [parc for parc in parcerias_salvas if parc.oferta and parc.inicio is not None]
    return ofertas


if __name__ == "__main__":
    parcerias = get_parcerias()
    for parceria in parcerias:
        print(parceria)
