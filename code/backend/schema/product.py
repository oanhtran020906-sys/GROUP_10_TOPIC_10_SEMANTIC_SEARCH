# định nghĩa cấu trúc sản phẩm mà API sẽ trả về cho Frontend
from pydantic import BaseModel
from typing import Optional

class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str
    price: float
    image_path: Optional[str]
    description: Optional[str]
    category_id: int
    budget_id: Optional[int] = None 
    similarity_score: Optional[float] = None
    search_type: Optional[str] = None

    class Config:
        from_attributes = True