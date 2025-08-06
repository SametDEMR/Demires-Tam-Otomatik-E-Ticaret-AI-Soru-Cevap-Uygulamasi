using Demires.Data;
using Demires.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Demires.Controllers
{
    public class CagrilarController : Controller
    {
        private readonly AppDbContext _context;

        public CagrilarController(AppDbContext context)
        {
            _context = context;
        }

        public IActionResult AdminCagrilar()
        {
            var model = new
            {
                UncategorizedCalls = _context.Cagrilar.FromSqlRaw("SELECT * FROM Çağrılar WHERE DepartmanID = 1").ToList(),
                UnansweredCalls = _context.Cagrilar.FromSqlRaw("SELECT * FROM Çağrılar WHERE Durum = 1 AND DepartmanID != 1").ToList(),
                AnsweredCalls = _context.Cagrilar.FromSqlRaw("SELECT * FROM Çağrılar WHERE Durum = 0").ToList()
            };
            return View(model);
        }

        [HttpGet]
        public async Task<IActionResult> GetCallData()
        {
            var model = new
            {
                UncategorizedCalls = _context.Cagrilar.FromSqlRaw("SELECT * FROM Çağrılar WHERE DepartmanID = 1").ToList(),
                UnansweredCalls = _context.Cagrilar.FromSqlRaw("SELECT * FROM Çağrılar WHERE Durum = 1 AND DepartmanID != 1").ToList(),
                AnsweredCalls = _context.Cagrilar.FromSqlRaw("SELECT * FROM Çağrılar WHERE Durum = 0").ToList()
            };
            return Json(model);
        }
    }
}