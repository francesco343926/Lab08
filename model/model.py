from database.impianto_DAO import ImpiantoDAO
from statistics import median

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''


class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese: int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        # TODO
        impianti = self._impianti
        medie = []
        for impianto in impianti:
            consumiMese = []
            impianto.get_consumi()
            consumiTotali = impianto.lista_consumi
            for consumo in consumiTotali:
                if consumo.data.month == mese:
                    consumiMese.append(consumo)
            valori = []
            for consumo in consumiMese:
                valori.append(consumo.kwh)
            media = median(valori)
            medie.append((impianto.nome, media))
        return medie

    def get_sequenza_ottima(self, mese: int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in
                         enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        # TODO

        if len(sequenza_parziale) == 7:
            self.__sequenza_ottima = sequenza_parziale
            self.__costo_ottimo = costo_corrente
            return

        if giorno == 1:
            consumominimo = 10000
            for impianto in sorted(consumi_settimana):
                if consumi_settimana[impianto][0].kwh < consumominimo:
                    consumominimo = consumi_settimana[impianto][0].kwh
                    ultimo_impianto = consumi_settimana[impianto][0].id_impianto
            costo_corrente = consumominimo
            self.__ricorsione(sequenza_parziale=sequenza_parziale + [ultimo_impianto],
                              giorno=giorno + 1,
                              ultimo_impianto=ultimo_impianto,
                              costo_corrente=costo_corrente,
                              consumi_settimana=consumi_settimana)

        else:
            costo_corrente1 = 0
            costo_corrente2 = 0
            altroimpianto = ""
            for impianto in sorted(consumi_settimana):
                if consumi_settimana[impianto][giorno - 1].id_impianto != ultimo_impianto:
                    costo_corrente1 = costo_corrente + 5 + consumi_settimana[impianto][giorno - 1].kwh
                    altroimpianto = consumi_settimana[impianto][giorno - 1].id_impianto
                else:
                    costo_corrente2 = costo_corrente + consumi_settimana[impianto][giorno - 1].kwh
            costo_corrente = min(costo_corrente1, costo_corrente2)
            if costo_corrente == costo_corrente1:
                ultimo_impianto = altroimpianto
            self.__ricorsione(sequenza_parziale=sequenza_parziale + [ultimo_impianto],
                              giorno=giorno + 1,
                              ultimo_impianto=ultimo_impianto,
                              costo_corrente=costo_corrente,
                              consumi_settimana=consumi_settimana)

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        # TODO
        consumi = dict()
        for impianto in self._impianti:
            lista = []
            for consumo in impianto.lista_consumi:
                if consumo.data.month == mese:
                    if consumo.data.day < 8:
                        lista.append(consumo)
            consumi[impianto.nome] = lista
        return consumi
