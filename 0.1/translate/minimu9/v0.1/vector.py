def Vector_Dot_Product(vector1, vector2):
    op = 0.0
    for i in range(0,3):
        op += vector1[i] * vector2[i]
    return op

##Computes the cross product of two vectors
def Vector_Cross_Product(v1, v2):
    vectorOut = [0.0, 0.0, 0.0]
    vectorOut[0] = (v1[1] * v2[2]) - (v1[2] * v2[1]) 
    vectorOut[1] = (v1[2] * v2[0]) - (v1[0] * v2[2]) 
    vectorOut[2] = (v1[0] * v2[1]) - (v1[1] * v2[0]) 
    return vectorOut

##Multiply the vector by a scalar. 
def Vector_Scale(vectorIn, scale2):
    VectorOut = [0.0, 0.0, 0.0]
    for i in range(0, 3):
        VectorOut[i] = vectorIn[i] * scale2
    return VectorOut

##Add two vectors. 
def Vector_Add(vectorIn1, vectorIn2):
    vectorOut = [0.0, 0.0, 0.0]
    for i in range(0, 3):
        vectorOut[i] = vectorIn1[i] + vectorIn2[i]
    return vectorOut

