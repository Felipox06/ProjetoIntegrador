drop schema if exists defaultdb;

create schema defaultdb;
use defaultdb;

-- TABELA PROFESSORES
DROP TABLE IF EXISTS professores CASCADE;
CREATE TABLE professores (
  prof_RA VARCHAR(10) PRIMARY KEY,
  nome_prof VARCHAR(50),
  senha_prof VARCHAR(6),
  email_prof VARCHAR(30)
);

-- TABELA ALUNOS
DROP TABLE IF EXISTS alunos CASCADE;
CREATE TABLE alunos (
  aluno_RA VARCHAR(10) PRIMARY KEY,
  nome_aluno VARCHAR(50),
  serie VARCHAR(15) NOT NULL,
  senha_aluno VARCHAR(6),
  pont_total DECIMAL(15,2) NULL
);

-- TABELA ESTATISTICA
DROP TABLE IF EXISTS estatistica CASCADE;
CREATE TABLE estatistica (
  id_estatistica INT PRIMARY KEY,
  total_jogos INT NOT NULL,
  total_questoes INT NOT NULL
);

-- TABELA JOGOS
DROP TABLE IF EXISTS jogos CASCADE;
CREATE TABLE jogos (
  id_jogos INT PRIMARY KEY,
  pontuacao_obtida DECIMAL(15,2),
  pontuacao_garantida DECIMAL(15,2),
  pontuacao_atual DECIMAL(15,2),
  aluno_RA VARCHAR(10),
  FOREIGN KEY (aluno_RA) REFERENCES alunos(aluno_RA)
    ON DELETE CASCADE ON UPDATE CASCADE
);

-- TABELA HISTÓRICO JOGOS
DROP TABLE IF EXISTS hist_jogos CASCADE;
CREATE TABLE hist_jogos (
  id_hist_jogos INT PRIMARY KEY,
  data_inicio DATE NOT NULL,
  data_fim DATE NOT NULL,
  resultado VARCHAR(29) NOT NULL,
  id_jogos INT,
  aluno_RA VARCHAR(10),
  id_estatistica INT,
  FOREIGN KEY (id_jogos) REFERENCES jogos(id_jogos)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (aluno_RA) REFERENCES alunos(aluno_RA)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_estatistica) REFERENCES estatistica(id_estatistica)
    ON DELETE CASCADE ON UPDATE CASCADE
);

-- TABELA SERIE
DROP TABLE IF EXISTS serie CASCADE;
CREATE TABLE series (
  id_serie INT PRIMARY KEY,
  nome_serie VARCHAR(20),
  aluno_RA VARCHAR(10),
  FOREIGN KEY (aluno_RA) REFERENCES alunos(aluno_RA)
);

-- TABELA TURMA
DROP TABLE IF EXISTS turma CASCADE;
CREATE TABLE turmas(
id_turma INT PRIMARY KEY,
letra CHAR(1),
id_serie INT,
aluno_RA VARCHAR(10),
FOREIGN KEY (id_serie) REFERENCES series(id_serie),
FOREIGN KEY (aluno_RA) REFERENCES alunos(aluno_RA)
);


-- TABELA MATERIAS
DROP TABLE IF EXISTS materias CASCADE;
CREATE TABLE materias (
  id_materia INT PRIMARY KEY,
  nome_materia VARCHAR(25) NOT NULL,
  descricao TINYTEXT NULL
);

-- TABELA DIFICULDADES
DROP TABLE IF EXISTS dificuldades CASCADE;
CREATE TABLE dificuldades (
  id_dificuldade INT PRIMARY KEY,
  nome_dificuldade ENUM('fácil', 'média', 'difícil') NOT NULL
);

-- TABELA QUESTÕES
DROP TABLE IF EXISTS questoes CASCADE;
CREATE TABLE questoes (
  id_questao INT PRIMARY KEY AUTO_INCREMENT,
  enunciado_questao TEXT NOT NULL,
  dicas TINYTEXT NOT NULL,
  id_materia INT,
  id_dificuldade INT,
  id_serie INT,
  prof_RA VARCHAR(10),
  FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_dificuldade) REFERENCES dificuldades(id_dificuldade)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (prof_RA) REFERENCES professores(prof_RA)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (id_serie) REFERENCES series(id_serie)
);

-- TABELA ALTERNATIVAS
DROP TABLE IF EXISTS alternativas CASCADE;
CREATE TABLE alternativas (
  id_alt INT PRIMARY KEY,
  letra CHAR(1) NOT NULL,
  texto_alt MEDIUMTEXT NOT NULL,
  correta BOOLEAN NOT NULL,
  id_questao INT,
  FOREIGN KEY (id_questao) REFERENCES questoes(id_questao)
    ON DELETE CASCADE ON UPDATE CASCADE
);

-- TABELA QUESTÕES JOGO
DROP TABLE IF EXISTS questoes_jogo CASCADE;
CREATE TABLE questoes_jogo (
  id_questoes_jogo INT PRIMARY KEY,
  nivel_questao INT,
  valor_questao DECIMAL(15,2) NOT NULL,
  acertou BOOLEAN,
  dica_usada BOOLEAN,
  id_questao INT,
  id_alt INT,
  id_jogos INT,
  aluno_RA VARCHAR(10),
  FOREIGN KEY (id_questao) REFERENCES questoes(id_questao)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_alt) REFERENCES alternativas(id_alt)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (id_jogos) REFERENCES jogos(id_jogos)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (aluno_RA) REFERENCES alunos(aluno_RA)
    ON DELETE CASCADE ON UPDATE CASCADE
);