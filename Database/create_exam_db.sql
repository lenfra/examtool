-- Creator:       MySQL Workbench 6.3.8/ExportSQLite Plugin 0.1.0
-- Author:        Lennart Franked
-- Caption:       Exam_DB
-- Project:       ExamTool
-- Changed:       2017-07-25 12:09
-- Created:       2016-03-22 16:01
PRAGMA foreign_keys = OFF;

-- Schema: ExamDB
-- ATTACH "ExamDB.sdb" AS 
BEGIN;
CREATE TABLE "Bibliography"(
  "bibliography_id" VARCHAR(64) PRIMARY KEY NOT NULL,
  "data" VARCHAR(4096) DEFAULT NULL,
  "tags" VARCHAR(256) DEFAULT NULL
);
CREATE TABLE "Document_Classes"(
  "document_class_id" VARCHAR(15) PRIMARY KEY NOT NULL,
  "class" VARCHAR(45) DEFAULT NULL,
  "options" VARCHAR(45) DEFAULT NULL
);
CREATE TABLE "Graphics"(
  "graphics_id" VARCHAR(256) PRIMARY KEY NOT NULL,
  "uri" VARCHAR(4096) NOT NULL,
  CONSTRAINT "uri_UNIQUE"
    UNIQUE("uri")
);
CREATE TABLE "Counters"(
  "type" VARCHAR(45) NOT NULL,
  "ident" VARCHAR(45) NOT NULL,
  "counter_value" VARCHAR(5) NOT NULL,
  PRIMARY KEY("type","ident")
);
CREATE TABLE "Authors"(
  "author_id" VARCHAR(6) PRIMARY KEY NOT NULL,
  "name" VARCHAR(45) DEFAULT NULL,
  "email" VARCHAR(45) DEFAULT NULL,
  "phone" VARCHAR(45) DEFAULT NULL
);
CREATE TABLE "Packages"(
  "package_id" VARCHAR(15) PRIMARY KEY NOT NULL,
  "package" VARCHAR(45) DEFAULT NULL,
  "options" VARCHAR(128) DEFAULT NULL
);
CREATE TABLE "Instructions"(
  "instruction_id" VARCHAR(15) PRIMARY KEY NOT NULL,
  "language" VARCHAR(3) DEFAULT NULL,
  "data" VARCHAR(1024) DEFAULT NULL
);
CREATE TABLE "Default_Packages"(
  "default_package_id" VARCHAR(15) NOT NULL,
  "package_id" VARCHAR(15) NOT NULL,
  PRIMARY KEY("default_package_id","package_id"),
  CONSTRAINT "fk_defaultPackages_Packages1"
    FOREIGN KEY("package_id")
    REFERENCES "Packages"("package_id")
);
CREATE INDEX "Default_Packages.fk_defaultPackages_Packages1_idx" ON "Default_Packages" ("package_id");
CREATE TABLE "Declarations"(
  "declaration_id" VARCHAR(15) PRIMARY KEY NOT NULL,
  "data" VARCHAR(1024) DEFAULT NULL,
  "tags" VARCHAR(256) DEFAULT NULL
);
CREATE TABLE "Course"(
  "course_code" VARCHAR(6) NOT NULL,
  "course_name_swe" VARCHAR(45) DEFAULT NULL,
  "course_name_eng" VARCHAR(45) DEFAULT NULL,
  "course_credits" VARCHAR(5) DEFAULT NULL,
  "course_progression" CHAR(4) DEFAULT NULL,
  "course_version" FLOAT NOT NULL,
  PRIMARY KEY("course_code","course_version")
);
CREATE TABLE "Questions"(
  "question_id" VARCHAR(15) PRIMARY KEY NOT NULL,
  "language" CHAR(3) DEFAULT NULL,
  "points" VARCHAR(45) DEFAULT NULL,
  "question" VARCHAR(8184) DEFAULT NULL,
  "answer" VARCHAR(8184) DEFAULT NULL,
  "usable" BOOL DEFAULT NULL,
  "feedback" TEXT(8184),
  "tags" VARCHAR(128)
);
CREATE TABLE "Question_has_Declaration_Requirement"(
  "question_id" VARCHAR(15) NOT NULL,
  "declaration_id" VARCHAR(15) NOT NULL,
  PRIMARY KEY("question_id","declaration_id"),
  CONSTRAINT "fk_QuestionDeclarationRequirement_Declarations1"
    FOREIGN KEY("declaration_id")
    REFERENCES "Declarations"("declaration_id"),
  CONSTRAINT "fk_QuestionDeclarationRequirement_Questions1"
    FOREIGN KEY("question_id")
    REFERENCES "Questions"("question_id")
);
CREATE INDEX "Question_has_Declaration_Requirement.fk_QuestionDeclarationRequirement_Declarations1_idx" ON "Question_has_Declaration_Requirement" ("declaration_id");
CREATE TABLE "ILO"(
  "goal" VARCHAR(15) NOT NULL,
  "course_code" VARCHAR(6) NOT NULL,
  "course_version" FLOAT NOT NULL,
  "description" VARCHAR(256) DEFAULT NULL,
  "tags" VARCHAR(128) DEFAULT NULL,
  PRIMARY KEY("goal","course_code","course_version"),
  CONSTRAINT "fk_CourseGoals_Course1"
    FOREIGN KEY("course_code","course_version")
    REFERENCES "Course"("course_code","course_version")
);
CREATE INDEX "ILO.fk_CourseGoals_Course1_idx" ON "ILO" ("course_code","course_version");
CREATE TABLE "Questions_has_Graphics"(
  "question_id" VARCHAR(15) NOT NULL,
  "graphics_id" VARCHAR(256) NOT NULL,
  PRIMARY KEY("question_id","graphics_id"),
  CONSTRAINT "fk_Questions_has_Images_Questions1"
    FOREIGN KEY("question_id")
    REFERENCES "Questions"("question_id"),
  CONSTRAINT "fk_Questions_has_Images_Images1"
    FOREIGN KEY("graphics_id")
    REFERENCES "Graphics"("graphics_id")
);
CREATE INDEX "Questions_has_Graphics.fk_Questions_has_Images_Images1_idx" ON "Questions_has_Graphics" ("graphics_id");
CREATE INDEX "Questions_has_Graphics.fk_Questions_has_Images_Questions1_idx" ON "Questions_has_Graphics" ("question_id");
CREATE TABLE "Question_has_Package_Requirement"(
  "question_id" VARCHAR(15) NOT NULL,
  "package_id" VARCHAR(15) NOT NULL,
  "options" VARCHAR(128) DEFAULT NULL,
  PRIMARY KEY("question_id","package_id"),
  CONSTRAINT "fk_QuestionPackageRequirement_Packages1"
    FOREIGN KEY("package_id")
    REFERENCES "Packages"("package_id"),
  CONSTRAINT "fk_QuestionPackageRequirement_Questions1"
    FOREIGN KEY("question_id")
    REFERENCES "Questions"("question_id")
);
CREATE INDEX "Question_has_Package_Requirement.fk_QuestionPackageRequirement_Packages1_idx" ON "Question_has_Package_Requirement" ("package_id");

CREATE TABLE "Questions_Not_In_Same_Exam"(
  "question_id" VARCHAR(15) NOT NULL,
  "question_id_similar" VARCHAR(15) NOT NULL,
  PRIMARY KEY("question_id","question_id_similar"),
  CONSTRAINT "fk_QuestionsNotInSameExam_Questions1"
    FOREIGN KEY("question_id")
    REFERENCES "Questions"("question_id"),
  CONSTRAINT "fk_QuestionsNotInSameExam_Questions2"
    FOREIGN KEY("question_id_similar")
    REFERENCES "Questions"("question_id")
);
CREATE INDEX "Questions_Not_In_Same_Exam.fk_QuestionsNotInSameExam_Questions2_idx" ON "Questions_Not_In_Same_Exam" ("question_id_similar");
CREATE TABLE "Profile"(
  "course_code" VARCHAR(6) NOT NULL,
  "course_version" FLOAT NOT NULL,
  "instruction_id" VARCHAR(15),
  "document_class_id" VARCHAR(15),
  "default_package_id" VARCHAR(15),
  "author_id" VARCHAR(6),
  "goal" VARCHAR(15),
  "exam_aids" VARCHAR(255),
  "exam_type" VARCHAR(45),
  "time_limit" VARCHAR(20),
  "language" VARCHAR(3),
  "number_of_questions" INTEGER,
  "exam_date" DATE,
  "grade_limits" VARCHAR(255),
  "grade_comment" VARCHAR(512),
  "allow_same_tags" BOOL,
  PRIMARY KEY("course_code","course_version"),
  CONSTRAINT "fk_Profile_Course1"
    FOREIGN KEY("course_code","course_version")
    REFERENCES "Course"("course_code","course_version"),
  CONSTRAINT "fk_Profile_Instructions1"
    FOREIGN KEY("instruction_id")
    REFERENCES "Instructions"("instruction_id"),
  CONSTRAINT "fk_Profile_DocumentClasses1"
    FOREIGN KEY("document_class_id")
    REFERENCES "Document_Classes"("document_class_id"),
  CONSTRAINT "fk_Profile_DefaultPackages1"
    FOREIGN KEY("default_package_id")
    REFERENCES "Default_Packages"("default_package_id"),
  CONSTRAINT "fk_Profile_Authors1"
    FOREIGN KEY("author_id")
    REFERENCES "Authors"("author_id"),
  CONSTRAINT "fk_Profile_CourseGoals1"
    FOREIGN KEY("goal")
    REFERENCES "ILO"("goal")
);
CREATE INDEX "Profile.fk_Profile_Instructions1_idx" ON "Profile" ("instruction_id");
CREATE INDEX "Profile.fk_Profile_DocumentClasses1_idx" ON "Profile" ("document_class_id");
CREATE INDEX "Profile.fk_Profile_DefaultPackages1_idx" ON "Profile" ("default_package_id");
CREATE INDEX "Profile.fk_Profile_Authors1_idx" ON "Profile" ("author_id");
CREATE INDEX "Profile.fk_Profile_CourseGoals1_idx" ON "Profile" ("goal");
CREATE TABLE "Questions_has_ILO"(
  "question_id" VARCHAR(15) NOT NULL,
  "goal" VARCHAR(15) NOT NULL,
  "course_code" VARCHAR(6) NOT NULL,
  "course_version" FLOAT NOT NULL,
  PRIMARY KEY("question_id","goal","course_code","course_version"),
  CONSTRAINT "fk_Questions_has_CourseGoals_CourseGoals1"
    FOREIGN KEY("goal","course_code","course_version")
    REFERENCES "ILO"("goal","course_code","course_version"),
  CONSTRAINT "fk_Questions_has_CourseGoals_Questions1"
    FOREIGN KEY("question_id")
    REFERENCES "Questions"("question_id")
);
CREATE INDEX "Questions_has_ILO.fk_Questions_has_CourseGoals_CourseGoals1_idx" ON "Questions_has_ILO" ("goal","course_code","course_version");
CREATE INDEX "Questions_has_ILO.fk_Questions_has_CourseGoals_Questions1_idx" ON "Questions_has_ILO" ("question_id");
CREATE TABLE "Exams"(
  "exam_id" VARCHAR(15) NOT NULL,
  "course_code" VARCHAR(6) NOT NULL,
  "course_version" FLOAT NOT NULL,
  "exam_date" DATE DEFAULT NULL,
  "language" VARCHAR(3) DEFAULT NULL,
  "time_limit" VARCHAR(20) DEFAULT NULL,
  "exam_aids" VARCHAR(255) DEFAULT NULL,
  "grade_limits" VARCHAR(255) DEFAULT NULL,
  "exam_type" VARCHAR(45) DEFAULT NULL,
  "grade_comment" VARCHAR(512),
  PRIMARY KEY("exam_id","course_code","course_version"),
  CONSTRAINT "fk_Exams_Course1"
    FOREIGN KEY("course_code","course_version")
    REFERENCES "Course"("course_code","course_version")
);
CREATE INDEX "Exams.fk_Exams_Course1_idx" ON "Exams" ("course_code","course_version");
CREATE TABLE "Question_has_Bibliography_Requirement"(
  "question_id" VARCHAR(15) NOT NULL,
  "bibliography_id" VARCHAR(64) NOT NULL,
  "optional" VARCHAR(45) DEFAULT NULL,
  PRIMARY KEY("question_id","bibliography_id"),
  CONSTRAINT "fk_Questions_has_Bibliography_Bibliography1"
    FOREIGN KEY("bibliography_id")
    REFERENCES "Bibliography"("bibliography_id"),
  CONSTRAINT "fk_Questions_has_Bibliography_Questions1"
    FOREIGN KEY("question_id")
    REFERENCES "Questions"("question_id")
);
CREATE INDEX "Question_has_Bibliography_Requirement.fk_Questions_has_Bibliography_Bibliography1_idx" ON "Question_has_Bibliography_Requirement" ("bibliography_id");
CREATE INDEX "Question_has_Bibliography_Requirement.fk_Questions_has_Bibliography_Questions1_idx" ON "Question_has_Bibliography_Requirement" ("question_id");
CREATE TABLE "Exam_Authors"(
  "author_id" VARCHAR(6) NOT NULL,
  "exam_id" VARCHAR(15) NOT NULL,
  PRIMARY KEY("author_id","exam_id"),
  CONSTRAINT "fk_AuthorsExam_Authors1"
    FOREIGN KEY("author_id")
    REFERENCES "Authors"("author_id"),
  CONSTRAINT "fk_AuthorsExam_Exams1"
    FOREIGN KEY("exam_id")
    REFERENCES "Exams"("exam_id")
);
CREATE INDEX "Exam_Authors.fk_AuthorsExam_Authors1_idx" ON "Exam_Authors" ("author_id");
CREATE INDEX "Exam_Authors.fk_AuthorsExam_Exams1_idx" ON "Exam_Authors" ("exam_id");
CREATE TABLE "Exam_Results"(
  "exam_id" VARCHAR(15) NOT NULL,
  "question_id" VARCHAR(15) NOT NULL,
  "student_id" VARCHAR(45) NOT NULL,
  "points" VARCHAR(45),
  "custom_feedback" VARCHAR(2048),
  PRIMARY KEY("exam_id","question_id","student_id"),
  CONSTRAINT "fk_Exams_has_Questions_Exams1"
    FOREIGN KEY("exam_id")
    REFERENCES "Exams"("exam_id"),
  CONSTRAINT "fk_Exams_has_Questions_Questions1"
    FOREIGN KEY("question_id")
    REFERENCES "Questions"("question_id")
);
CREATE INDEX "Exam_Results.fk_Exams_has_Questions_Questions1_idx" ON "Exam_Results" ("question_id");
CREATE INDEX "Exam_Results.fk_Exams_has_Questions_Exams1_idx" ON "Exam_Results" ("exam_id");
CREATE TABLE "Preamble"(
  "exam_id" VARCHAR(15) NOT NULL,
  "instruction_id" VARCHAR(15) NOT NULL,
  "document_class_id" VARCHAR(15) NOT NULL,
  "default_package_id" VARCHAR(15) NOT NULL,
  PRIMARY KEY("exam_id","instruction_id","document_class_id","default_package_id"),
  CONSTRAINT "fk_Preamble_DocumentClasses1"
    FOREIGN KEY("document_class_id")
    REFERENCES "Document_Classes"("document_class_id"),
  CONSTRAINT "fk_Preamble_Exams1"
    FOREIGN KEY("exam_id")
    REFERENCES "Exams"("exam_id"),
  CONSTRAINT "fk_Preamble_Instructions1"
    FOREIGN KEY("instruction_id")
    REFERENCES "Instructions"("instruction_id"),
  CONSTRAINT "fk_Preamble_defaultPackages1"
    FOREIGN KEY("default_package_id")
    REFERENCES "Default_Packages"("default_package_id")
);
CREATE INDEX "Preamble.fk_Preamble_Instructions1_idx" ON "Preamble" ("instruction_id");
CREATE INDEX "Preamble.fk_Preamble_DocumentClasses1_idx" ON "Preamble" ("document_class_id");
CREATE INDEX "Preamble.fk_Preamble_defaultPackages1_idx" ON "Preamble" ("default_package_id");
CREATE INDEX "Preamble.fk_Preamble_Exams1_idx" ON "Preamble" ("exam_id");
CREATE TABLE "Questions_in_Exam"(
  "exam_id" VARCHAR(15) NOT NULL,
  "question_id" VARCHAR(15) NOT NULL,
  "order" INTEGER,
  PRIMARY KEY("exam_id","question_id"),
  CONSTRAINT "fk_OldExams_Exams1"
    FOREIGN KEY("exam_id")
    REFERENCES "Exams"("exam_id"),
  CONSTRAINT "fk_OldExams_Questions1"
    FOREIGN KEY("question_id")
    REFERENCES "Questions"("question_id")
);
CREATE INDEX "Questions_in_Exam.fk_OldExams_Exams1_idx" ON "Questions_in_Exam" ("exam_id");
CREATE INDEX "Questions_in_Exam.fk_OldExams_Questions1_idx" ON "Questions_in_Exam" ("question_id");
COMMIT;
