CREATE DATABASE IF NOT EXISTS nido_peluches
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE nido_peluches;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS peluches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    usuario_id INT NOT NULL,
    adoptado BOOLEAN NOT NULL DEFAULT FALSE,
    adoptado_por INT DEFAULT NULL,
    visitas INT NOT NULL DEFAULT 0,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_peluche_donante FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_peluche_adoptante FOREIGN KEY (adoptado_por) REFERENCES usuarios(id) ON DELETE SET NULL,
    INDEX idx_peluche_usuario (usuario_id),
    INDEX idx_peluche_adoptado (adoptado)
) ENGINE=InnoDB;
