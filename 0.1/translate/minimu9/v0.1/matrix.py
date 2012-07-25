def Matrix_Multiply(matrixa, matrixb):
    matrixOut = [ [ 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0 ] ]
    temp = [0.0, 0.0, 0.0]
    for x in range(0, 3):
        for y in range(0, 3):
            for z in range(0, 3):
                temp[z] = matrixa[x][z] * matrixb[z][y]
            matrixOut[x][y] = 0.0
            matrixOut[x][y] = temp[0] + temp[1] + temp[2]
    
    return matrixOut

