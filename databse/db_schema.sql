drop schema if exists defaultdb;

create schema defaultdb;
use defaultdb;

-- TABELA PROFESSORES
DROP TABLE IF EXISTS professores CASCADE;
CREATE TABLE professores (
  prof_RA VARCHAR(10) PRIMARY KEY,
  nome_prof VARCHAR(50),
  senha_prof VARCHAR(6),
  id_materia INT,
  FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
);

-- TABELA ALUNOS
DROP TABLE IF EXISTS alunos CASCADE;
CREATE TABLE alunos (
  aluno_RA VARCHAR(10) PRIMARY KEY,
  nome_aluno VARCHAR(50),
  turma VARCHAR(15) NOT NULL,
  senha_aluno VARCHAR(6),
  pont_total DECIMAL(15,2) NULL
);

-- TABELA ESTATISTICA
DROP TABLE IF EXISTS estatisticas_jogos;
CREATE TABLE estatisticas_jogos (
    id_estatistica_jogo INT AUTO_INCREMENT PRIMARY KEY,
    aluno_RA VARCHAR(10) NOT NULL,             
    id_materia INT NOT NULL,                  
    serie_jogo VARCHAR(20) NOT NULL,
    pontuacao_obtida_jogo INT NOT NULL,        
    questoes_respondidas_partida INT NOT NULL,
    acertos_partida INT NOT NULL,
    data_jogo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (aluno_RA) REFERENCES alunos(aluno_RA)
        ON DELETE CASCADE ON UPDATE CASCADE, 
        FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
        ON DELETE RESTRICT ON UPDATE CASCADE   
);

-- TABELA SERIE
DROP TABLE IF EXISTS turmas CASCADE;
CREATE TABLE turmas (
  id_turma INT PRIMARY KEY AUTO_INCREMENT,
  nome_turma VARCHAR(50) NOT NULL,
  serie_turma VARCHAR(20) NOT NULL,
  periodo_turma VARCHAR(20) NOT NULL,
  ano_letivo YEAR NOT NULL
);

-- TABELA MATERIAS
DROP TABLE IF EXISTS materias CASCADE;
CREATE TABLE materias (
  id_materia INT PRIMARY KEY,
  nome_materia VARCHAR(30) NOT NULL
);

-- TABELA DIFICULDADES
DROP TABLE IF EXISTS dificuldades CASCADE;
CREATE TABLE dificuldades (
  id_dificuldade INT PRIMARY KEY,
  nome_dificuldade VARCHAR(20) UNIQUE NOT NULL
);

-- TABELA SERIE
DROP TABLE IF EXISTS serie CASCADE;
CREATE TABLE serie(
id_serie INT PRIMARY KEY AUTO_INCREMENT,
nome_serie VARCHAR(20) UNIQUE NOT NULL
);

-- TABELA QUESTÕES
DROP TABLE IF EXISTS questoes CASCADE;
CREATE TABLE questoes (
  id_questao INT PRIMARY KEY AUTO_INCREMENT,
  id_materia INT,
  id_dificuldade INT,
  id_serie INT NOT NULL,
  enunciado TEXT NOT NULL,
  explicacao TEXT NOT NULL,
  alternativa_1 TEXT NOT NULL,
  alternativa_2 TEXT NOT NULL,
  alternativa_3 TEXT NOT NULL,
  alternativa_4 TEXT NOT NULL,
  indice_alternativa_correta TINYINT NOT NULL,
  FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (id_dificuldade) REFERENCES dificuldades(id_dificuldade)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (id_serie) REFERENCES serie(id_serie)
    ON DELETE RESTRICT ON UPDATE CASCADE
);