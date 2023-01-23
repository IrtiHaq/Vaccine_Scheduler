CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caresgivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE APPOINTMENT (
    APID int PRIMARY KEY,
    Patient varchar(255) REFERENCES Patients,
    Vaccine varchar(255) REFERENCES Vaccines,
    Time date NOT NULL,
    Caregiver varchar(255) NOT NULL,
    FOREIGN KEY (Caregiver) REFERENCES Caregivers(Username),
    CONSTRAINT freeapmt UNIQUE(Time, Caregiver)
);