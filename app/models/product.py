from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    stock_quantity = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    low_stock_threshold = Column(Integer, default=10, nullable=False)

    category_id = Column(Integer, ForeignKey("categories.id"))
    unit_of_measure_id = Column(Integer, ForeignKey("units_of_measure.id"))

    category = relationship("Category", back_populates="products")
    unit_of_measure = relationship("UnitOfMeasure", back_populates="products")
