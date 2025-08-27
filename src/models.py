from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    String, Boolean, Integer, ForeignKey,
    CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        Index("ix_users_email", "email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(80))
    last_name: Mapped[str | None] = mapped_column(String(80))
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)

    
    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
        
        }



class Planet(db.Model):
    __tablename__ = "planets"
    __table_args__ = (
        UniqueConstraint("name", name="uq_planets_name"),
        Index("ix_planets_name", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    climate: Mapped[str | None] = mapped_column(String(80))   
    terrain: Mapped[str | None] = mapped_column(String(80))   
    population: Mapped[int | None] = mapped_column(Integer)   


    favorites: Mapped[list["Favorite"]] = relationship(back_populates="planet")
    residents: Mapped[list["Character"]] = relationship(
        back_populates="homeworld"
    )

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population,
        }

class Character(db.Model):
    __tablename__ = "characters"
    __table_args__ = (
        UniqueConstraint("name", name="uq_characters_name"),
        Index("ix_characters_name", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    species: Mapped[str | None] = mapped_column(String(80))
    gender: Mapped[str | None] = mapped_column(String(20))       
    birth_year: Mapped[str | None] = mapped_column(String(20))   
    homeworld_id: Mapped[int | None] = mapped_column(
        ForeignKey("planets.id"), nullable=True
    )


    homeworld: Mapped["Planet"] = relationship(back_populates="residents")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="character")

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "gender": self.gender,
            "birth_year": self.birth_year,
            "homeworld_id": self.homeworld_id,
        }



class Favorite(db.Model):
    __tablename__ = "favorites"
    __table_args__ = (
        
        CheckConstraint(
            "(planet_id IS NOT NULL AND character_id IS NULL) OR "
            "(planet_id IS NULL AND character_id IS NOT NULL)",
            name="ck_favorite_exactly_one_target",
        ),
        
        UniqueConstraint("user_id", "planet_id", name="uq_user_planet_fav"),
        UniqueConstraint("user_id", "character_id", name="uq_user_character_fav"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    planet_id: Mapped[int | None] = mapped_column(ForeignKey("planets.id"))
    character_id: Mapped[int | None] = mapped_column(ForeignKey("characters.id"))

    
    user: Mapped["User"] = relationship(back_populates="favorites")
    planet: Mapped["Planet"] = relationship(back_populates="favorites")
    character: Mapped["Character"] = relationship(back_populates="favorites")

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "character_id": self.character_id,
        }


if __name__ == "__main__":
    try:
        from eralchemy2 import render_er
        render_er(db.Model.metadata, "diagram.png")
        print("✅ Diagrama generado como diagram.png")
    except Exception as e:
        print("❌ Error al generar el diagrama:", e)
        raise
