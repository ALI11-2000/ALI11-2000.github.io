def alu_model(a:int,b:int,sel:int):
    #ALU Model for simple arithmetic calculations
    X=[a+b,abs(int(a-b)),a+b,(a) & (b), (a) | (b),(a) ^ (b),a,b]
    #Performing comparison between the two numbers
    if(sel==2):
        if(int(a)>int(b)):
            return 1
        else:
            return 0
    return X[sel]