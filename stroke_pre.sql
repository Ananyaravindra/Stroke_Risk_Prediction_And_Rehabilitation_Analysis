--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

-- Started on 2025-01-31 15:38:09

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 222 (class 1259 OID 49358)
-- Name: exercise; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercise (
    exercise_id integer NOT NULL,
    user_id integer,
    exercise_type character varying(100) NOT NULL,
    duration integer NOT NULL,
    date date NOT NULL,
    logged_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.exercise OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 49357)
-- Name: exercise_exercise_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exercise_exercise_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exercise_exercise_id_seq OWNER TO postgres;

--
-- TOC entry 4825 (class 0 OID 0)
-- Dependencies: 221
-- Name: exercise_exercise_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exercise_exercise_id_seq OWNED BY public.exercise.exercise_id;


--
-- TOC entry 220 (class 1259 OID 49345)
-- Name: medication; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.medication (
    med_id integer NOT NULL,
    user_id integer,
    med_name character varying(100) NOT NULL,
    dosage character varying(50) NOT NULL,
    schedule character varying(50) NOT NULL,
    logged_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.medication OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 49344)
-- Name: medication_med_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.medication_med_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.medication_med_id_seq OWNER TO postgres;

--
-- TOC entry 4827 (class 0 OID 0)
-- Dependencies: 219
-- Name: medication_med_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.medication_med_id_seq OWNED BY public.medication.med_id;


--
-- TOC entry 218 (class 1259 OID 49335)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    name character varying(100) NOT NULL,
    age integer NOT NULL,
    gender character varying(10) NOT NULL,
    email character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 49334)
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- TOC entry 4829 (class 0 OID 0)
-- Dependencies: 217
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- TOC entry 4656 (class 2604 OID 49361)
-- Name: exercise exercise_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise ALTER COLUMN exercise_id SET DEFAULT nextval('public.exercise_exercise_id_seq'::regclass);


--
-- TOC entry 4654 (class 2604 OID 49348)
-- Name: medication med_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medication ALTER COLUMN med_id SET DEFAULT nextval('public.medication_med_id_seq'::regclass);


--
-- TOC entry 4652 (class 2604 OID 49338)
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- TOC entry 4818 (class 0 OID 49358)
-- Dependencies: 222
-- Data for Name: exercise; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exercise (exercise_id, user_id, exercise_type, duration, date, logged_at) FROM stdin;
1	1	Running	30	2025-01-31	2025-01-31 15:20:49.23248
2	2	Cycling	45	2025-01-30	2025-01-31 15:20:49.23248
\.


--
-- TOC entry 4816 (class 0 OID 49345)
-- Dependencies: 220
-- Data for Name: medication; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.medication (med_id, user_id, med_name, dosage, schedule, logged_at) FROM stdin;
1	1	Aspirin	75mg	Morning	2025-01-31 15:20:49.23248
2	2	Metformin	500mg	Evening	2025-01-31 15:20:49.23248
\.


--
-- TOC entry 4814 (class 0 OID 49335)
-- Dependencies: 218
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, name, age, gender, email, created_at) FROM stdin;
1	John Doe	45	Male	johndoe@example.com	2025-01-31 15:20:49.23248
2	Jane Smith	30	Female	janesmith@example.com	2025-01-31 15:20:49.23248
\.


--
-- TOC entry 4830 (class 0 OID 0)
-- Dependencies: 221
-- Name: exercise_exercise_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exercise_exercise_id_seq', 2, true);


--
-- TOC entry 4831 (class 0 OID 0)
-- Dependencies: 219
-- Name: medication_med_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.medication_med_id_seq', 2, true);


--
-- TOC entry 4832 (class 0 OID 0)
-- Dependencies: 217
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 2, true);


--
-- TOC entry 4665 (class 2606 OID 49364)
-- Name: exercise exercise_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise
    ADD CONSTRAINT exercise_pkey PRIMARY KEY (exercise_id);


--
-- TOC entry 4663 (class 2606 OID 49351)
-- Name: medication medication_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medication
    ADD CONSTRAINT medication_pkey PRIMARY KEY (med_id);


--
-- TOC entry 4659 (class 2606 OID 49343)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4661 (class 2606 OID 49341)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- TOC entry 4667 (class 2606 OID 49365)
-- Name: exercise exercise_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercise
    ADD CONSTRAINT exercise_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 4666 (class 2606 OID 49352)
-- Name: medication medication_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.medication
    ADD CONSTRAINT medication_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 4824 (class 0 OID 0)
-- Dependencies: 222
-- Name: TABLE exercise; Type: ACL; Schema: public; Owner: postgres
--

GRANT INSERT,DELETE,UPDATE ON TABLE public.exercise TO stroke_user;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.exercise TO "s.user";


--
-- TOC entry 4826 (class 0 OID 0)
-- Dependencies: 220
-- Name: TABLE medication; Type: ACL; Schema: public; Owner: postgres
--

GRANT INSERT,DELETE,UPDATE ON TABLE public.medication TO stroke_user;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.medication TO "s.user";


--
-- TOC entry 4828 (class 0 OID 0)
-- Dependencies: 218
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT INSERT,DELETE,UPDATE ON TABLE public.users TO stroke_user;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.users TO "s.user";


--
-- TOC entry 2054 (class 826 OID 49333)
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT INSERT,DELETE,UPDATE ON TABLES TO stroke_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO "s.user";


-- Completed on 2025-01-31 15:38:09

--
-- PostgreSQL database dump complete
--

