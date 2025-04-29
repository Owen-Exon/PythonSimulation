import math
from math import pi

def MathTypeErrorText(operandType:str,object1,object2):
    return f"unsupported operand type(s) for {operandType}: '{type(object1).__name__}' and '{type(object2).__name__}'"



def solveQuadratic(quadratic_a:float,quadratic_b:float,quadratic_c:float) -> list[float]:
    
    """Returns the two roots of a quadratic given its coefficients.

    Args:
        quadratic_a (float) : The x^2 coefficient
        quadratic_b (float) : The x^1 coefficient
        quadratic_c (float) : The x^0 coefficient

    Returns:
        list[float]: The list is always exactly two items long, one for each root
    """
    
    discriminant = (quadratic_b ** 2) - (4 * quadratic_a * quadratic_c)
    
    if discriminant < 0 :
        return ValueError("Imaginary Roots")
    
    root1 = ((-quadratic_b + math.sqrt(discriminant)) / (2 * quadratic_a))
    root2 = ((-quadratic_b - math.sqrt(discriminant)) / (2 * quadratic_a))
    return root1,root2



class Angle:
    
    """A class for working with angles"""
    
    def __init__(self,angle:float,angleType:str="Rad"):
        
        """Init an angle class

        Args:
            angle (float) : The magnitude of the angle
            angleType (str = "Deg" | "Rad") : The units for the value entered. Defaults to "Rad"
        
        """
                
        if angleType == "Deg":
            self.Angle = angle
        elif angleType == "Rad":
            self.Angle = (angle)*180/math.pi
    
    def degrees(self) -> float:
        """Returns the angle in degrees"""
        return self.Angle

    def rad(self) -> float:
        """Returns the angle in rad"""
        return (self.Angle)*math.pi/180
    
    def __str__(self):
        return f"{self.rad()} rad"
    
    def __add__(self,other):
        if isinstance(other,Angle):
            return Angle(self.rad() + other.rad())
        else:
            raise TypeError(MathTypeErrorText("+",self,other))
            
    def __sub__(self,other):
        if isinstance(other,Angle):
            return Angle(self.rad() - other.rad())
        else:
            raise TypeError(MathTypeErrorText("-",self,other))
            
    def __mul__(self,other):
        if isinstance(other,float|int):
            return Angle(other*self.rad())
        else:
            raise TypeError(MathTypeErrorText("*",self,other))
        
    def __rmul__(self,other):
        return self*other

    def __truediv__(self,other):
        if isinstance(other,float|int):
            return Angle(self.rad()/other)
        else:
            raise TypeError(MathTypeErrorText("/",self,other))



class Vector2D:
    """A class for working with 2D vectors"""
    
    def __init__(self, x:int|float|Angle, y:int|float):
        
        """Creates a Vector2D class
        
        Args:
            x (int|float|angle): if x is an int|float it is the x coordinate, if x is an angle, is the angle from +ve x axis
            y (int|float): if x is an int|float, it is the y coordinate, if x angle, it is the length of the 

        """
        
        if isinstance(x,Angle):
            self.x = math.cos(x.rad())*y
            self.y = math.sin(x.rad())*y
        else:
            self.x = x
            self.y = y
    
    def __str__(self):
        return f'({self.x} , {self.y})'
    
    def __call__(self) -> list[float]:
        """Returns the vector as a 2 item list"""
        return [self.x,self.y]
    
    def length(self) -> float:
        """Returns the length of the vector"""
        return math.sqrt((self.x**2)+(self.y**2))
    
    def angle(self) -> Angle:
        
        """Returns the angle of the vector from the +ve x axis"""
        
        return(Angle(math.atan2(self.y,self.x)))        
    
    def __add__(self,other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x + other.x , self.y + other.y)
        else:
            raise ValueError(MathTypeErrorText("+",self,other))
    
    def __sub__(self,other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x - other.x , self.y - other.y)
        else:
            raise ValueError(MathTypeErrorText("-",self,other))
    
    def __mul__(self,other):
        if isinstance(other, int|float):
            return Vector2D(self.x * other, self.y * other)
        else:
            raise ValueError(MathTypeErrorText("*",self,other))
    
    def __rmul__(self,other):
        return self*other

    def __truediv__(self,other):
        if isinstance(other, int|float):
            return Vector2D(self.x / other, self.y / other)
        else:
            raise ValueError(MathTypeErrorText("/",self,other))



def dotProduct(v1:Vector2D,v2:Vector2D) -> float|int:
    if isinstance(v1,Vector2D) & isinstance(v2,Vector2D):
        return v1.x * v2.x + v1.y * v2.y
    else:
        raise ValueError("Dot product must be done on two vectors")
