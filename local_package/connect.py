from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum
import datetime
import queue
import io

class TestWrapper(EWrapper):
    """
    The wrapper deals with the action coming back from the IB gateway or TWS instance
    We override methods in EWrapper that will get called when this action happens, like currentTime
    """
    def historicalData(self, reqId:int, bar):
        print ("Historical Data. ",reqId, "Date: ",bar.date,"Open:", bar.open, "High:", bar.high,"Low:", bar.low,"Close:", bar.close,"Vol:",bar.volume)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

    def historicalDataUpdate(self, reqId: int, bar):
        print("HistoricalDataUpdate. ReqId:", reqId, "BarData.", bar)
    ## error handling code
    def init_error(self):
        error_queue=queue.Queue()
        self._my_errors = error_queue

    def get_error(self, timeout=5):
        if self.is_error():
            try:
                return self._my_errors.get(timeout=timeout)
            except queue.Empty:
                return None

        return None


    def is_error(self):
        an_error_if=not self._my_errors.empty()
        return an_error_if

    def error(self, id, errorCode, errorString):
        ## Overriden method
        errormsg = "IB error id %d errorcode %d string %s" % (id, errorCode, errorString)
        self._my_errors.put(errormsg)

    ## Time telling code
    def init_time(self):
        time_queue=queue.Queue()
        self._time_queue = time_queue

        return time_queue

    def currentTime(self, time_from_server):
        ## Overriden method
        self._time_queue.put(time_from_server)





class TestClient(EClient):
    """
    The client method
    We don't override native methods, but instead call them from our own wrappers
    """
    def __init__(self, wrapper):
        self.msg_queue = queue.Queue()
        super().__init__(wrapper)

    def send(self, *fields):
        """Serialize and send the given fields using the IB socket protocol."""
        if not self.isConnected():
            raise ConnectionError('Not connected')

        msg = io.StringIO()
        for field in fields:
            typ = type(field)
            if field in (None, UNSET_INTEGER, UNSET_DOUBLE):
                s = ''
            elif typ in (str, int, float):
                s = str(field)
            elif typ is bool:
                s = '1' if field else '0'
            elif typ is list:
                # list of TagValue
                s = ''.join(f'{v.tag}={v.value};' for v in field)
            elif isinstance(field, Contract):
                c = field
                s = '\0'.join(str(f) for f in (
                    c.conId, c.symbol, c.secType,
                    c.lastTradeDateOrContractMonth, c.strike,
                    c.right, c.multiplier, c.exchange,
                    c.primaryExchange, c.currency,
                    c.localSymbol, c.tradingClass))
            else:
                s = str(field)
            msg.write(s)
            msg.write('\0')
        # self.sendMsg(msg.getvalue())
    def reqContractDetails(self, reqId, contract):
        self.send(
            9, 8, reqId, contract, contract.includeExpired,
            contract.secIdType, contract.secId)

class TestApp(TestWrapper,TestClient):
    """
    The wrapper deals with the action coming back from the IB gateway or TWS instance
    We override methods in EWrapper that will get called when this action happens, like currentTime
    Extra methods are added as we need to store the results in this object
    """

    def __init__(self):
        TestWrapper.__init__(self)
        TestClient.__init__(self, self)
        self.msg_queue.queue.append('---'*10)

    def error(self,reqId, errorCode, errorString):
        print ("Error:",reqId,"  ",errorCode,"  ",errorString)

    # def contractDetails(self, reqId, contractDetails):
    #     print ("contractDetails: ", reqId, "  ", contractDetails)
    #
    # def tickPrice(self,reqId, tickType, price, attrib):
    #     print ("Tick Price. Ticker ID: ", reqId, "tickType:", TickTypeEnum.to_str(tickType), " Price:",price, end=" ")

    # def historicalData(self,reqId, bar):
    #     # bardata=[bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume]
    #     # print ('__'*10)
    #     # return (bardata)
    #     print ("Historical Data. ",reqId, "Date: ",bar.date,"Open:", bar.open, "High:", bar.high,"Low:", bar.low,"Close:", bar.close,"Vol:",bar.volume)


def main():
    app = TestApp()
    app.connect("127.0.0.1",7497,0)


    contract = Contract()
    contract.symbol = "EUR"
    contract.secType = "CASH"
    contract.exchange = "IDEALPRO"
    contract.currency = "USD"



    # contract.symbol = "AAPL"
    # contract.secType = "STK"
    # contract.exchange = "SMART"
    # contract.currency = "USD"
    # contract.primaryExchange = "NASDAQ"

    # app.reqContractDetails(43,contract)

    app.reqHistoricalData(
    1, # tickerId,
    contract,
    "",
    "1 D",
    "1 day",
    "MIDPOINT",
    0,
    1,
    False, # KeepUpToDate
    [])





    app.run() # process self.msg_queue

if __name__ == "__main__":
    main()
