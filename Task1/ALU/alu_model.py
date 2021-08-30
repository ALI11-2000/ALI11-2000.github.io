

def alu_model(a:int,b:int,sel:int):
    X=[a+b,abs(int(a-b)),a+b,(a) & (b), (a) | (b),(a) ^ (b),a,b]
    if(sel==2):
        if(int(a)>int(b)):
            return 1
        else:
            return 0
    return X[sel]