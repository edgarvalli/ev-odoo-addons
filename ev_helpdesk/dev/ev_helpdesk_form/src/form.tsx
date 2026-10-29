export function HelpdeskForm() {
  return (
    <div className="container">
      <div className="row">
        <div className="col">
          <h1>Helpdesk Formulario</h1>
        </div>
        <div className="row">
          <div className="col">
            <label htmlFor="form-label">Titulo</label>
            <input type="text" className="form-control" />
          </div>
        </div>
        <div className="row">
          <div className="col">
            <button className="btn btn-primary">Enviar</button>
          </div>
        </div>
      </div>
    </div>
  );
}
