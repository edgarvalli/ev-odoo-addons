def empleado_query(dbname: str, kwargs: dict) -> tuple:
    query = f"""
        SELECT
            empleado.idempleado id,
            empleado.codigoempleado codigo,
            CONCAT(empleado.nombre,' ',empleado.apellidopaterno,' ' ,empleado.apellidomaterno) AS nombre,
            CONCAT(empleado.rfc, FORMAT(empleado.fechanacimiento, 'yyMMdd') ,empleado.homoclave) as rfc,
            CONCAT(empleado.curpi, FORMAT(empleado.fechanacimiento, 'yyMMdd') ,empleado.curpf) as curp,
            empleado.fechaalta,
            empleado.numerosegurosocial,
            empleado.codigopostal,
            CASE
                WHEN empleado.basecotizacionimss = 'F' THEN 'Fijo'
                WHEN empleado.basecotizacionimss = 'V' THEN 'Variable'
                WHEN empleado.basecotizacionimss = 'M' THEN 'Mixto'
            END AS tiposalario,
            CASE
                WHEN turno.TipoJornada = 1 THEN '01 Diurna'
                WHEN turno.TipoJornada = 2 THEN '02 Nocturna'
                WHEN turno.TipoJornada = 3 THEN '03 Mixta'
                WHEN turno.TipoJornada = 4 THEN '04 Por Hora'
            END AS jornada,
            puesto.descripcion puesto,
            departamentos.descripcion departamento,
            empleado.CorreoElectronico correo,
            empleado.sueldointegrado sbc,
            empleado.cidregistropatronal,
            empresa.GUIDDSL guiddsl,
            empresa.NombreEmpresaFiscal empresa
        FROM [{dbname}].dbo.nom10001 empleado
        INNER JOIN [{dbname}].dbo.NOM10006 puesto ON puesto.idpuesto = empleado.idpuesto
        INNER JOIN [{dbname}].dbo.NOM10032 turno ON empleado.idturno = turno.idturno
        INNER JOIN [{dbname}].dbo.NOM10003 departamentos ON departamentos.iddepartamento = empleado.iddepartamento
        LEFT JOIN [{dbname}].dbo.NOM10000 empresa ON empresa.GUIDEmpresa <> ''
    """

    rfc = kwargs.get("rfc")

    if rfc:
        query += f"""
            WHERE
            UPPER(CONCAT(empleado.rfc, FORMAT(empleado.fechanacimiento, 'yyMMdd') ,empleado.homoclave))
            = UPPER(?)
        """

        return query, (rfc,)

    email = kwargs.get("email")
    if email:
        query += f"\n WHERE empleado.CorreoElectronico = ?"
        return query, (email,)

    empleadoid = kwargs.get("empleadoid")
    if empleadoid:
        query += f"WHERE empleado.idempleado = ?"
        return query, (empleadoid,)

    codigoempleado = kwargs.get("codigoempleado")
    if codigoempleado:
        query += f"WHERE empleado.codigoempleado = ?"
        return query, (codigoempleado,)

    return query, ()
