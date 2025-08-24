--
-- PostgreSQL database dump
--

\restrict cg1cpEIu5bD5Ro8cS479Ih3ecX6hhVkbcz7AiBF0NhgZ0o3I6AEnZmr1FigV2F8

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

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

--
-- Name: gen_calendario_cuotas(smallint); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.gen_calendario_cuotas(p_venta_id smallint) RETURNS void
    LANGUAGE plpgsql
    AS $$
begin
  perform public.gen_calendario_cuotas(p_venta_id::bigint);
end$$;


ALTER FUNCTION public.gen_calendario_cuotas(p_venta_id smallint) OWNER TO postgres;

--
-- Name: gen_calendario_cuotas(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.gen_calendario_cuotas(p_venta_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
begin
  perform public.gen_calendario_cuotas(p_venta_id::bigint);
end$$;


ALTER FUNCTION public.gen_calendario_cuotas(p_venta_id integer) OWNER TO postgres;

--
-- Name: gen_calendario_cuotas(bigint); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.gen_calendario_cuotas(p_venta_id bigint) RETURNS void
    LANGUAGE plpgsql
    AS $$
declare
  v_fecha_venta date;
  v_precio_venta numeric(12,2);
  v_adelanto    numeric(12,2);
  v_cant        int;
  v_dia_venc    int;
  i             int;
  monto_base    numeric(12,2);
  valor_cuota   numeric(12,2);
  venc          date;
  last_dom      date;
begin
  -- Traigo la venta
  select fecha_venta, precio_venta, adelanto, cant_cuotas, dia_venc
    into v_fecha_venta, v_precio_venta, v_adelanto, v_cant, v_dia_venc
  from public.ventas
  where venta_id = p_venta_id;

  if not found then
    raise exception 'Venta % no existe', p_venta_id;
  end if;

  -- Limpio calendario anterior (si existe)
  delete from public.calendario_pagos where venta_id = p_venta_id;

  monto_base := coalesce(v_precio_venta,0) - coalesce(v_adelanto,0);
  if coalesce(v_cant,0) <= 0 then
    return;
  end if;

  valor_cuota := round(monto_base / v_cant, 2);

  for i in 1..v_cant loop
    -- Vencimiento del mes i (respetando d¡a de vencimiento y l¡mite del mes)
    venc := (date_trunc('month', v_fecha_venta)::date + make_interval(months => i));
    last_dom := (date_trunc('month', venc) + interval '1 month - 1 day')::date;
    venc := make_date(extract(year from venc)::int, extract(month from venc)::int, 1)
            + (v_dia_venc - 1) * interval '1 day';
    venc := least(venc::date, last_dom);

    insert into public.calendario_pagos
      (venta_id, nro_cuota, fecha_venc, importe_cuota, estado_cuota, dias_atraso, monto_pendiente)
    values
      (p_venta_id, i, venc, valor_cuota, 'Pendiente', 0, valor_cuota);
  end loop;
end
$$;


ALTER FUNCTION public.gen_calendario_cuotas(p_venta_id bigint) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: calendario_pagos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.calendario_pagos (
    cuota_id bigint NOT NULL,
    venta_id bigint NOT NULL,
    nro_cuota integer NOT NULL,
    fecha_venc date NOT NULL,
    importe_cuota numeric(12,2) NOT NULL,
    estado_cuota text DEFAULT 'Pendiente'::text,
    dias_atraso integer DEFAULT 0,
    monto_pendiente numeric(12,2) DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT calendario_pagos_dias_atraso_check CHECK ((dias_atraso >= 0)),
    CONSTRAINT calendario_pagos_importe_cuota_check CHECK ((importe_cuota >= (0)::numeric)),
    CONSTRAINT calendario_pagos_monto_pendiente_check CHECK ((monto_pendiente >= (0)::numeric)),
    CONSTRAINT calendario_pagos_nro_cuota_check CHECK ((nro_cuota > 0))
);


ALTER TABLE public.calendario_pagos OWNER TO postgres;

--
-- Name: calendario_pagos_cuota_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.calendario_pagos_cuota_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.calendario_pagos_cuota_id_seq OWNER TO postgres;

--
-- Name: calendario_pagos_cuota_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.calendario_pagos_cuota_id_seq OWNED BY public.calendario_pagos.cuota_id;


--
-- Name: clientes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clientes (
    cliente_id bigint NOT NULL,
    nombre text NOT NULL,
    apellido text NOT NULL,
    dni character varying(15) NOT NULL,
    telefono character varying(20),
    email text,
    direccion text,
    ciudad text,
    created_at timestamp with time zone DEFAULT now(),
    tel_whatsapp character varying(20)
);


ALTER TABLE public.clientes OWNER TO postgres;

--
-- Name: clientes_cliente_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clientes_cliente_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clientes_cliente_id_seq OWNER TO postgres;

--
-- Name: clientes_cliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clientes_cliente_id_seq OWNED BY public.clientes.cliente_id;


--
-- Name: cobranzas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cobranzas (
    cobranza_id bigint NOT NULL,
    cuota_id bigint NOT NULL,
    fecha_pago date DEFAULT CURRENT_DATE NOT NULL,
    monto_pagado numeric(12,2) NOT NULL,
    metodo_pago text DEFAULT 'Efectivo'::text,
    observaciones text,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT cobranzas_monto_pagado_check CHECK ((monto_pagado >= (0)::numeric))
);


ALTER TABLE public.cobranzas OWNER TO postgres;

--
-- Name: cobranzas_cobranza_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cobranzas_cobranza_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cobranzas_cobranza_id_seq OWNER TO postgres;

--
-- Name: cobranzas_cobranza_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cobranzas_cobranza_id_seq OWNED BY public.cobranzas.cobranza_id;


--
-- Name: dispositivos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dispositivos (
    dispositivo_id bigint NOT NULL,
    nombre text NOT NULL,
    descripcion text,
    precio_base numeric(12,2) NOT NULL,
    stock integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    marca text,
    modelo text,
    color text,
    precio_lista numeric(12,2),
    costo numeric(12,2),
    descuento_pct numeric(5,2) DEFAULT 0,
    descuento numeric(6,2) DEFAULT 0,
    CONSTRAINT dispositivos_descuento_check CHECK ((descuento >= (0)::numeric)),
    CONSTRAINT dispositivos_descuento_pct_check CHECK (((descuento_pct >= (0)::numeric) AND (descuento_pct <= (100)::numeric))),
    CONSTRAINT dispositivos_precio_base_check CHECK ((precio_base >= (0)::numeric)),
    CONSTRAINT dispositivos_stock_check CHECK ((stock >= 0))
);


ALTER TABLE public.dispositivos OWNER TO postgres;

--
-- Name: dispositivos_dispositivo_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dispositivos_dispositivo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dispositivos_dispositivo_id_seq OWNER TO postgres;

--
-- Name: dispositivos_dispositivo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dispositivos_dispositivo_id_seq OWNED BY public.dispositivos.dispositivo_id;


--
-- Name: planes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.planes (
    plan_id integer NOT NULL,
    nombre text NOT NULL
);


ALTER TABLE public.planes OWNER TO postgres;

--
-- Name: planes_cuotas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.planes_cuotas (
    plan_id bigint NOT NULL,
    nombre_plan text NOT NULL,
    cant_cuotas integer NOT NULL,
    tasa_nominal numeric(6,3) DEFAULT 0,
    cft numeric(6,3) DEFAULT 0,
    dia_venc integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    dia_venc_default integer,
    CONSTRAINT planes_cuotas_cant_cuotas_check CHECK ((cant_cuotas > 0)),
    CONSTRAINT planes_cuotas_cft_check CHECK ((cft >= (0)::numeric)),
    CONSTRAINT planes_cuotas_dia_venc_check CHECK (((dia_venc >= 1) AND (dia_venc <= 28))),
    CONSTRAINT planes_cuotas_tasa_nominal_check CHECK ((tasa_nominal >= (0)::numeric))
);


ALTER TABLE public.planes_cuotas OWNER TO postgres;

--
-- Name: planes_cuotas_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.planes_cuotas_plan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.planes_cuotas_plan_id_seq OWNER TO postgres;

--
-- Name: planes_cuotas_plan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.planes_cuotas_plan_id_seq OWNED BY public.planes_cuotas.plan_id;


--
-- Name: planes_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.planes_plan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.planes_plan_id_seq OWNER TO postgres;

--
-- Name: planes_plan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.planes_plan_id_seq OWNED BY public.planes.plan_id;


--
-- Name: roles_permisos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles_permisos (
    permiso_id bigint NOT NULL,
    rol text NOT NULL,
    modulo text NOT NULL,
    puede_ver boolean DEFAULT true,
    puede_crear boolean DEFAULT false,
    puede_editar boolean DEFAULT false,
    puede_borrar boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.roles_permisos OWNER TO postgres;

--
-- Name: roles_permisos_permiso_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_permisos_permiso_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_permisos_permiso_id_seq OWNER TO postgres;

--
-- Name: roles_permisos_permiso_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_permisos_permiso_id_seq OWNED BY public.roles_permisos.permiso_id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    usuario_id bigint NOT NULL,
    nombre text NOT NULL,
    email text NOT NULL,
    password text NOT NULL,
    rol text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT usuarios_rol_check CHECK ((rol = ANY (ARRAY['admin'::text, 'vendedor'::text, 'cobranzas'::text])))
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- Name: usuarios_usuario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuarios_usuario_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_usuario_id_seq OWNER TO postgres;

--
-- Name: usuarios_usuario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_usuario_id_seq OWNED BY public.usuarios.usuario_id;


--
-- Name: ventas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ventas (
    venta_id bigint NOT NULL,
    fecha_venta date DEFAULT CURRENT_DATE NOT NULL,
    cliente_id bigint NOT NULL,
    dispositivo_id bigint NOT NULL,
    precio_venta numeric(12,2) NOT NULL,
    adelanto numeric(12,2) DEFAULT 0,
    plan_id bigint NOT NULL,
    cant_cuotas integer NOT NULL,
    tasa_nominal numeric(6,3) DEFAULT 0,
    cft numeric(6,3) DEFAULT 0,
    dia_venc integer NOT NULL,
    estado_venta text DEFAULT 'Activa'::text,
    created_at timestamp with time zone DEFAULT now(),
    descuento_pct numeric(5,2) DEFAULT 0,
    CONSTRAINT ventas_adelanto_check CHECK ((adelanto >= (0)::numeric)),
    CONSTRAINT ventas_cant_cuotas_check CHECK ((cant_cuotas > 0)),
    CONSTRAINT ventas_cft_check CHECK ((cft >= (0)::numeric)),
    CONSTRAINT ventas_descuento_pct_check CHECK (((descuento_pct >= (0)::numeric) AND (descuento_pct <= (100)::numeric))),
    CONSTRAINT ventas_dia_venc_check CHECK (((dia_venc >= 1) AND (dia_venc <= 28))),
    CONSTRAINT ventas_precio_venta_check CHECK ((precio_venta >= (0)::numeric)),
    CONSTRAINT ventas_tasa_nominal_check CHECK ((tasa_nominal >= (0)::numeric))
);


ALTER TABLE public.ventas OWNER TO postgres;

--
-- Name: ventas_venta_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ventas_venta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ventas_venta_id_seq OWNER TO postgres;

--
-- Name: ventas_venta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ventas_venta_id_seq OWNED BY public.ventas.venta_id;


--
-- Name: calendario_pagos cuota_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calendario_pagos ALTER COLUMN cuota_id SET DEFAULT nextval('public.calendario_pagos_cuota_id_seq'::regclass);


--
-- Name: clientes cliente_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes ALTER COLUMN cliente_id SET DEFAULT nextval('public.clientes_cliente_id_seq'::regclass);


--
-- Name: cobranzas cobranza_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cobranzas ALTER COLUMN cobranza_id SET DEFAULT nextval('public.cobranzas_cobranza_id_seq'::regclass);


--
-- Name: dispositivos dispositivo_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispositivos ALTER COLUMN dispositivo_id SET DEFAULT nextval('public.dispositivos_dispositivo_id_seq'::regclass);


--
-- Name: planes plan_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planes ALTER COLUMN plan_id SET DEFAULT nextval('public.planes_plan_id_seq'::regclass);


--
-- Name: planes_cuotas plan_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planes_cuotas ALTER COLUMN plan_id SET DEFAULT nextval('public.planes_cuotas_plan_id_seq'::regclass);


--
-- Name: roles_permisos permiso_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles_permisos ALTER COLUMN permiso_id SET DEFAULT nextval('public.roles_permisos_permiso_id_seq'::regclass);


--
-- Name: usuarios usuario_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN usuario_id SET DEFAULT nextval('public.usuarios_usuario_id_seq'::regclass);


--
-- Name: ventas venta_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ventas ALTER COLUMN venta_id SET DEFAULT nextval('public.ventas_venta_id_seq'::regclass);


--
-- Data for Name: calendario_pagos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.calendario_pagos (cuota_id, venta_id, nro_cuota, fecha_venc, importe_cuota, estado_cuota, dias_atraso, monto_pendiente, created_at) FROM stdin;
1	3	1	2025-09-10	0.00	Pendiente	0	0.00	2025-08-23 04:35:47.815829+00
2	3	2	2025-10-10	0.00	Pendiente	0	0.00	2025-08-23 04:35:47.815829+00
3	3	3	2025-11-10	0.00	Pendiente	0	0.00	2025-08-23 04:35:47.815829+00
4	3	4	2025-12-10	0.00	Pendiente	0	0.00	2025-08-23 04:35:47.815829+00
5	3	5	2026-01-10	0.00	Pendiente	0	0.00	2025-08-23 04:35:47.815829+00
6	3	6	2026-02-10	0.00	Pendiente	0	0.00	2025-08-23 04:35:47.815829+00
7	3	7	2026-03-10	0.00	Pendiente	0	0.00	2025-08-23 04:35:47.815829+00
8	3	8	2026-04-10	0.00	Pendiente	0	0.00	2025-08-23 04:35:47.815829+00
9	3	9	2026-05-10	0.00	Pendiente	0	0.00	2025-08-23 04:35:47.815829+00
10	3	10	2026-06-10	0.00	Pendiente	0	0.00	2025-08-23 04:35:47.815829+00
11	3	11	2026-07-10	0.00	Pendiente	0	0.00	2025-08-23 04:35:47.815829+00
12	3	12	2026-08-10	0.00	Pendiente	0	0.00	2025-08-23 04:35:47.815829+00
13	11	1	2025-09-10	29166.67	Pendiente	0	29166.67	2025-08-24 20:04:07.079258+00
14	11	2	2025-10-10	29166.67	Pendiente	0	29166.67	2025-08-24 20:04:07.079258+00
15	11	3	2025-11-10	29166.67	Pendiente	0	29166.67	2025-08-24 20:04:07.079258+00
16	11	4	2025-12-10	29166.67	Pendiente	0	29166.67	2025-08-24 20:04:07.079258+00
17	11	5	2026-01-10	29166.67	Pendiente	0	29166.67	2025-08-24 20:04:07.079258+00
18	11	6	2026-02-10	29166.67	Pendiente	0	29166.67	2025-08-24 20:04:07.079258+00
19	11	7	2026-03-10	29166.67	Pendiente	0	29166.67	2025-08-24 20:04:07.079258+00
20	11	8	2026-04-10	29166.67	Pendiente	0	29166.67	2025-08-24 20:04:07.079258+00
21	11	9	2026-05-10	29166.67	Pendiente	0	29166.67	2025-08-24 20:04:07.079258+00
22	11	10	2026-06-10	29166.67	Pendiente	0	29166.67	2025-08-24 20:04:07.079258+00
23	11	11	2026-07-10	29166.67	Pendiente	0	29166.67	2025-08-24 20:04:07.079258+00
24	11	12	2026-08-10	29166.67	Pendiente	0	29166.67	2025-08-24 20:04:07.079258+00
\.


--
-- Data for Name: clientes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clientes (cliente_id, nombre, apellido, dni, telefono, email, direccion, ciudad, created_at, tel_whatsapp) FROM stdin;
1	Juan	P‚rez	40111222	1133344455	juan@example.com	Av. Siempre Viva 123	CABA	2025-08-23 00:47:20.358392+00	1133344455
2	Hernan	Rocca	25179209	\N	\N	Misiones 195	Caba	2025-08-23 04:07:39.855762+00	3416810017
\.


--
-- Data for Name: cobranzas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cobranzas (cobranza_id, cuota_id, fecha_pago, monto_pagado, metodo_pago, observaciones, created_at) FROM stdin;
\.


--
-- Data for Name: dispositivos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dispositivos (dispositivo_id, nombre, descripcion, precio_base, stock, created_at, marca, modelo, color, precio_lista, costo, descuento_pct, descuento) FROM stdin;
4	Celular	A340	3000.00	100	2025-08-23 06:15:34.773854+00	Motorola	Motorola A45 	Negro	5000.00	460.00	36.00	0.00
5	TV	\N	700000.00	30	2025-08-23 19:21:51.636142+00	Noblex	LCD	Negro	500000.00	0.00	20.00	0.00
1	Samsung Galaxy A15	128GB - Negro	350000.00	19	2025-08-23 00:41:47.745641+00	Gen‚rica	Samsung Galaxy A15	Negro	35000.00	280000.00	10.00	0.00
\.


--
-- Data for Name: planes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.planes (plan_id, nombre) FROM stdin;
1	Plan Base
\.


--
-- Data for Name: planes_cuotas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.planes_cuotas (plan_id, nombre_plan, cant_cuotas, tasa_nominal, cft, dia_venc, created_at, dia_venc_default) FROM stdin;
1	12 cuotas fijas	12	50.000	0.000	10	2025-08-23 00:41:47.736999+00	10
2	12 cuotas fijas	12	50.000	0.000	10	2025-08-23 00:47:20.344729+00	10
\.


--
-- Data for Name: roles_permisos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles_permisos (permiso_id, rol, modulo, puede_ver, puede_crear, puede_editar, puede_borrar, created_at) FROM stdin;
1	admin	ventas	t	t	t	t	2025-08-23 00:38:04.519432+00
2	admin	clientes	t	t	t	t	2025-08-23 00:38:04.519432+00
3	admin	cobranzas	t	t	t	t	2025-08-23 00:38:04.519432+00
4	admin	dispositivos	t	t	t	t	2025-08-23 00:38:04.519432+00
5	admin	planes	t	t	t	t	2025-08-23 00:38:04.519432+00
6	admin	usuarios	t	t	t	t	2025-08-23 00:38:04.519432+00
7	vendedor	ventas	t	t	t	f	2025-08-23 00:38:04.529137+00
8	vendedor	clientes	t	t	t	f	2025-08-23 00:38:04.529137+00
9	vendedor	dispositivos	t	f	f	f	2025-08-23 00:38:04.529137+00
10	cobranzas	cobranzas	t	t	t	f	2025-08-23 00:38:04.534185+00
11	cobranzas	calendario_pagos	t	t	t	f	2025-08-23 00:38:04.534185+00
12	cobranzas	clientes	t	f	f	f	2025-08-23 00:38:04.534185+00
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (usuario_id, nombre, email, password, rol, created_at) FROM stdin;
1	Admin Principal	admin@crm.com	admin123	admin	2025-08-23 00:40:59.010276+00
2	Juan P‚rez	vendedor@crm.com	vendedor123	vendedor	2025-08-23 00:40:59.017674+00
3	Mar¡a L¢pez	cobranzas@crm.com	cobranzas123	cobranzas	2025-08-23 00:40:59.022166+00
\.


--
-- Data for Name: ventas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ventas (venta_id, fecha_venta, cliente_id, dispositivo_id, precio_venta, adelanto, plan_id, cant_cuotas, tasa_nominal, cft, dia_venc, estado_venta, created_at, descuento_pct) FROM stdin;
3	2025-08-23	2	1	0.00	0.00	1	12	50.000	0.000	10	Activa	2025-08-23 04:35:47.815829+00	0.00
11	2025-08-24	1	1	350000.00	0.00	1	12	50.000	0.000	10	Activa	2025-08-24 20:04:07.079258+00	0.00
\.


--
-- Name: calendario_pagos_cuota_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.calendario_pagos_cuota_id_seq', 24, true);


--
-- Name: clientes_cliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clientes_cliente_id_seq', 2, true);


--
-- Name: cobranzas_cobranza_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cobranzas_cobranza_id_seq', 1, false);


--
-- Name: dispositivos_dispositivo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dispositivos_dispositivo_id_seq', 5, true);


--
-- Name: planes_cuotas_plan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.planes_cuotas_plan_id_seq', 2, true);


--
-- Name: planes_plan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.planes_plan_id_seq', 1, true);


--
-- Name: roles_permisos_permiso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_permisos_permiso_id_seq', 12, true);


--
-- Name: usuarios_usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_usuario_id_seq', 3, true);


--
-- Name: ventas_venta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ventas_venta_id_seq', 11, true);


--
-- Name: calendario_pagos calendario_pagos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calendario_pagos
    ADD CONSTRAINT calendario_pagos_pkey PRIMARY KEY (cuota_id);


--
-- Name: clientes clientes_dni_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_dni_key UNIQUE (dni);


--
-- Name: clientes clientes_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_email_key UNIQUE (email);


--
-- Name: clientes clientes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_pkey PRIMARY KEY (cliente_id);


--
-- Name: cobranzas cobranzas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cobranzas
    ADD CONSTRAINT cobranzas_pkey PRIMARY KEY (cobranza_id);


--
-- Name: dispositivos dispositivos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispositivos
    ADD CONSTRAINT dispositivos_pkey PRIMARY KEY (dispositivo_id);


--
-- Name: planes_cuotas planes_cuotas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planes_cuotas
    ADD CONSTRAINT planes_cuotas_pkey PRIMARY KEY (plan_id);


--
-- Name: planes planes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planes
    ADD CONSTRAINT planes_pkey PRIMARY KEY (plan_id);


--
-- Name: roles_permisos roles_permisos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles_permisos
    ADD CONSTRAINT roles_permisos_pkey PRIMARY KEY (permiso_id);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (usuario_id);


--
-- Name: dispositivos ux_dispositivos_nombre; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispositivos
    ADD CONSTRAINT ux_dispositivos_nombre UNIQUE (nombre);


--
-- Name: ventas ventas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ventas
    ADD CONSTRAINT ventas_pkey PRIMARY KEY (venta_id);


--
-- Name: idx_calendario_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_calendario_estado ON public.calendario_pagos USING btree (estado_cuota);


--
-- Name: idx_calendario_venc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_calendario_venc ON public.calendario_pagos USING btree (fecha_venc);


--
-- Name: idx_calendario_venta; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_calendario_venta ON public.calendario_pagos USING btree (venta_id);


--
-- Name: idx_clientes_dni; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clientes_dni ON public.clientes USING btree (dni);


--
-- Name: idx_clientes_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clientes_email ON public.clientes USING btree (email);


--
-- Name: idx_cobranzas_cuota; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cobranzas_cuota ON public.cobranzas USING btree (cuota_id);


--
-- Name: idx_cobranzas_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cobranzas_fecha ON public.cobranzas USING btree (fecha_pago);


--
-- Name: idx_planes_cuotas; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_planes_cuotas ON public.planes_cuotas USING btree (cant_cuotas);


--
-- Name: idx_roles_modulo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_roles_modulo ON public.roles_permisos USING btree (rol, modulo);


--
-- Name: idx_usuario_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_usuario_email ON public.usuarios USING btree (email);


--
-- Name: idx_ventas_cliente; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ventas_cliente ON public.ventas USING btree (cliente_id);


--
-- Name: idx_ventas_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ventas_estado ON public.ventas USING btree (estado_venta);


--
-- Name: idx_ventas_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ventas_fecha ON public.ventas USING btree (fecha_venta);


--
-- Name: ux_dispositivos_nombre_ci; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_dispositivos_nombre_ci ON public.dispositivos USING btree (lower(nombre));


--
-- Name: calendario_pagos calendario_pagos_venta_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.calendario_pagos
    ADD CONSTRAINT calendario_pagos_venta_id_fkey FOREIGN KEY (venta_id) REFERENCES public.ventas(venta_id) ON DELETE CASCADE;


--
-- Name: cobranzas cobranzas_cuota_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cobranzas
    ADD CONSTRAINT cobranzas_cuota_id_fkey FOREIGN KEY (cuota_id) REFERENCES public.calendario_pagos(cuota_id) ON DELETE CASCADE;


--
-- Name: ventas ventas_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ventas
    ADD CONSTRAINT ventas_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.planes_cuotas(plan_id);


--
-- PostgreSQL database dump complete
--

\unrestrict cg1cpEIu5bD5Ro8cS479Ih3ecX6hhVkbcz7AiBF0NhgZ0o3I6AEnZmr1FigV2F8

