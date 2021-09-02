CREATE TABLE "DimArea" (
  "Id" varchar PRIMARY KEY,
  "Type" varchar NOT NULL,
  "Name" varchar NOT NULL,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "DimArtist" (
  "Id" varchar PRIMARY KEY,
  "Type" varchar NOT NULL,
  "Name" varchar NOT NULL,
  "Country" varchar,
  "Disambiguation" varchar,
  "Gender" varchar,
  "Begin" date,
  "End" date,
  "Ended" boolean,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "DimInputartistInputtrack" (
  "InputArtist" varchar NOT NULL,
  "InputTrack" varchar NOT NULL
);

CREATE TABLE "DimLabel" (
  "Id" varchar PRIMARY KEY,
  "Type" varchar,
  "Name" varchar NOT NULL,
  "Code" integer,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "DimLabelType" (
  "Id" varchar PRIMARY KEY,
  "Type" varchar NOT NULL,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "DimRecord" (
  "Id" varchar PRIMARY KEY,
  "Title" varchar NOT NULL,
  "Disambiguation" varchar,
  "Video" boolean,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "DimRecordCreatorType" (
  "Id" varchar PRIMARY KEY,
  "Type" varchar,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "DimWork" (
  "Id" varchar PRIMARY KEY,
  "Type" varchar,
  "Title" varchar NOT NULL,
  "Language" varchar,
  "Iswc" varchar,
  "Disambiguation" varchar,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "DimWorkCreatorType" (
  "Id" varchar PRIMARY KEY,
  "Type" varchar NOT NULL,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "MappingArtistAlias" (
  "ArtistKey" varchar,
  "AliasName" varchar NOT NULL,
  "AliasType" varchar,
  "AliasLocale" varchar,
  "AliasPrimary" varchar,
  "AliasBeginDate" datetime,
  "AliasEndData" datetime,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "MappingArtistArea" (
  "ArtistKey" varchar NOT NULL,
  "AreaKey" varchar NOT NULL,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "MappingArtistIpi" (
  "ArtistKey" varchar NOT NULL,
  "IPI" varchar NOT NULL,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "MappingArtistIsni" (
  "ArtistKey" varchar NOT NULL,
  "ISNI" varchar NOT NULL,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "MappingInputartistInputtrack" (
  "InputartistArtist" varchar NOT NULL,
  "InputtrackTrack" varchar NOT NULL,
  "ArtistKey" varchar NOT NULL
);

CREATE TABLE "MappingRecordArtist" (
  "RecordKey" varchar NOT NULL,
  "ArtistKey" varchar NOT NULL,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "MappingRecordCreator" (
  "RecordKey" varchar NOT NULL,
  "CreatorKey" varchar NOT NULL,
  "CreatorRoleKey" varchar NOT NULL,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "MappingRecordIsrc" (
  "RecordKey" varchar NOT NULL,
  "ISRC" varchar NOT NULL,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "MappingRecordLabel" (
  "RecordKey" varchar NOT NULL,
  "LabelKey" varchar NOT NULL,
  "LabelTypeKey" varchar NOT NULL,
  "LabelBegin" date NOT NULL,
  "LabelEng" date NOT NULL,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "MappingRecordWork" (
  "RecordKey" varchar NOT NULL,
  "WorkKey" varchar NOT NULL,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "MappingWorkAttribute" (
  "WorkKey" varchar PRIMARY KEY,
  "AttributeName" varchar NOT NULL,
  "AttributeValue" varchar NOT NULL,
  "Datestamp" datetime NOT NULL
);

CREATE TABLE "MappingWorkCreator" (
  "WorkKey" varchar NOT NULL,
  "CreatorKey" varchar NOT NULL,
  "CreatorRoleKey" varchar NOT NULL,
  "Datestamp" datetime NOT NULL
);

ALTER TABLE "DimArea" ADD FOREIGN KEY ("Id") REFERENCES "MappingArtistArea" ("AreaKey");

ALTER TABLE "DimArtist" ADD FOREIGN KEY ("Id") REFERENCES "MappingArtistArea" ("ArtistKey");

ALTER TABLE "DimArtist" ADD FOREIGN KEY ("Id") REFERENCES "MappingArtistAlias" ("ArtistKey");

ALTER TABLE "DimArtist" ADD FOREIGN KEY ("Id") REFERENCES "MappingArtistIsni" ("ArtistKey");

ALTER TABLE "DimArtist" ADD FOREIGN KEY ("Id") REFERENCES "MappingArtistIpi" ("ArtistKey");

ALTER TABLE "DimArtist" ADD FOREIGN KEY ("Id") REFERENCES "MappingRecordArtist" ("ArtistKey");

ALTER TABLE "DimRecord" ADD FOREIGN KEY ("Id") REFERENCES "MappingRecordArtist" ("RecordKey");

ALTER TABLE "DimRecord" ADD FOREIGN KEY ("Id") REFERENCES "MappingRecordLabel" ("RecordKey");

ALTER TABLE "DimLabel" ADD FOREIGN KEY ("Id") REFERENCES "MappingRecordLabel" ("LabelKey");

ALTER TABLE "DimLabelType" ADD FOREIGN KEY ("Id") REFERENCES "MappingRecordLabel" ("LabelTypeKey");

ALTER TABLE "DimRecord" ADD FOREIGN KEY ("Id") REFERENCES "MappingRecordIsrc" ("RecordKey");

ALTER TABLE "DimRecord" ADD FOREIGN KEY ("Id") REFERENCES "MappingRecordCreator" ("RecordKey");

ALTER TABLE "DimArtist" ADD FOREIGN KEY ("Id") REFERENCES "MappingRecordCreator" ("CreatorKey");

ALTER TABLE "DimRecordCreatorType" ADD FOREIGN KEY ("Id") REFERENCES "MappingRecordCreator" ("CreatorRoleKey");

ALTER TABLE "DimRecord" ADD FOREIGN KEY ("Id") REFERENCES "MappingRecordWork" ("RecordKey");

ALTER TABLE "DimWork" ADD FOREIGN KEY ("Id") REFERENCES "MappingRecordWork" ("WorkKey");

ALTER TABLE "DimWork" ADD FOREIGN KEY ("Id") REFERENCES "MappingWorkAttribute" ("WorkKey");

ALTER TABLE "DimWork" ADD FOREIGN KEY ("Id") REFERENCES "MappingWorkCreator" ("WorkKey");

ALTER TABLE "DimArtist" ADD FOREIGN KEY ("Id") REFERENCES "MappingWorkCreator" ("CreatorKey");

ALTER TABLE "DimWorkCreatorType" ADD FOREIGN KEY ("Id") REFERENCES "MappingWorkCreator" ("CreatorRoleKey");

ALTER TABLE "DimInputartistInputtrack" ADD FOREIGN KEY ("InputArtist") REFERENCES "MappingInputartistInputtrack" ("InputartistArtist");

ALTER TABLE "DimInputartistInputtrack" ADD FOREIGN KEY ("InputTrack") REFERENCES "MappingInputartistInputtrack" ("InputtrackTrack");

ALTER TABLE "DimArtist" ADD FOREIGN KEY ("Id") REFERENCES "MappingInputartistInputtrack" ("ArtistKey");
