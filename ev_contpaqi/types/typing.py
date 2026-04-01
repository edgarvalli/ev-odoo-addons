from __future__ import annotations
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from hr.models.hr_employee import HrEmployee as _HrEmployee
    from hr.models.hr_department import HrDepartment as _HrDepartment
    from hr.models.hr_job import HrJob as _HrJob

    HrEmployee: TypeAlias = _HrEmployee
    HrDepartment: TypeAlias = _HrDepartment
    HrJob: TypeAlias = _HrJob
else:
    from odoo.addons.hr.models.hr_employee import HrEmployee
    from odoo.addons.hr.models.hr_department import HrDepartment
    from odoo.addons.hr.models.hr_job import HrJob
