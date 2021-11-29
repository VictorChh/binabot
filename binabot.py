from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
client = Client("abUxBTqZ2cNGh8piGILw2gvcWxtYRAqNLor8dDXvD1xcfI2oAKD2bCNOnzoaFHXd", "dTrdPU7dXGdM2SqdgAcMw7UGVFPLwHIetnvlqZiAeXzS7CDjTugp9Ifez9rv85ZQ")

import json
import pandas as pd
import datetime
import time
from binance.enums import *

def main():
    print("hello")
    for i in range(240):
        orders = client.get_all_margin_orders(symbol='BATUSDT', isIsolated='TRUE')
        df = pd.DataFrame.from_records(orders)
        df['time'] = pd.to_datetime(df["time"],unit='ms')
        df['updateTime'] = pd.to_datetime(df["updateTime"],unit='ms')
        df.tail(3)
        #el dataframe abiertas solo se ejecuta la primera vez para llevar control de las ordenes
        if i==0:
            abiertas = df[df["status"].isin(['NEW'])]
        abiertas2 = df[df["status"].isin(['NEW'])]
        print("")
        print ("----------------------- Ordenes abiertas ----------------------")
        print("")
        print(abiertas2)
        print("")
        print ("---------------- Ordenes abiertas actualizadas-----------------")
        print("")
        print(abiertas)
        abiertas3 = abiertas2[~abiertas2["orderId"].isin(abiertas["orderId"])]
        abiertas = pd.concat([abiertas,  abiertas3])

        for row in abiertas.orderId:
            orden= df[df['orderId'].isin([row])]

            x=orden['status'].astype(str)
            ordenId=row
            symbol=orden.symbol.values[0]
            side=orden.side.values[0]
            status=orden.status.values[0]
            price=float(orden.price.values[0])
            price=round(price, 4)
            quantity=float(orden.origQty.values[0])
            print("Evaluando orden: ",row)
    
            #evaluamos si alguna orden abierta cambio de estatus
            if 'FILLED' in x.values:
                #remplaza la orden de venta ejecutada por una nueva de venta
                if side == 'BUY':
                    nprice = price*1.02
                    print("")
                    print("Procesando orden: Venta" ,)
                    #print("Orden Side: " , orden.side)
                    print("Cantidad: " , quantity)
                    print("Precio" , nprice)
                    try:
                        crea_orden_venta(symbol,nprice,quantity)
                    except:
                        print("No se pudo crear la orden")
                    else:
                        print("Se creo una orden de venta")
                        #eliminar orden completada de ordenes abiertas
                        abiertas.drop(abiertas[abiertas["orderId"].isin([orderId])].index, inplace=True)
                        
                #remplaza la orden de compra ejecutada por una nueva de venta
                if side == 'SELL':
                    nprice = price*.98
                    print("")
                    print("Procesando orden: " , side)
                    #print("Orden Side: " , orden.side)
                    print("Cantidad: " , quantity)
                    print("Precio" , nprice)
                    try:
                        crea_orden_compra(symbol,nprice,quantity)
                    except:
                        print("No se pudo crear la orden")
                    else:
                        print("Se creo una orden de compra")
                        abiertas.drop(abiertas[abiertas["orderId"].isin([orden])].index, inplace=True)
            elif 'CANCELLED' in x.values:
                abiertas.drop(abiertas[abiertas["orderId"].isin([orden])].index, inplace=True)
            else:
                print(" No hubo actualización")

        print("")
        print ("-----------------------Termina proceso", i ,"----------------")
        print("")
        time.sleep(15)
    
def crea_orden_compra(symbol,price,quantity) :
    order = client.create_margin_order(
        symbol=symbol,
        side=SIDE_BUY,
        isIsolated='TRUE',
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=quantity,
        price=price)
    
def crea_orden_venta(symbol,price,quantity) :
    order = client.create_margin_order(
        symbol=symbol,
        side=SIDE_SELL,
        isIsolated='TRUE',
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=quantity,
        price=price)
if __name__ == '__main__':
    main()
