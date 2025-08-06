using Demires.Data;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Demires.Controllers
{
    public class GirisEkraniController : Controller
    {
        private readonly IConfiguration _configuration;
        private readonly AppDbContext _context;

        public GirisEkraniController(IConfiguration configuration, AppDbContext context)
        {
            _configuration = configuration;
            _context = context;
        }

        public IActionResult GirisEkrani()
        {
            return View();
        }

        [HttpPost]
        public IActionResult GirisYap(string kullaniciAdi, string sifre)
        {
            // JOIN kullanarak tek sorguda verileri çekme
            var kullanici = _context.Kullanici
                .FromSqlRaw(@"SELECT k.* FROM Kullanici k 
                     WHERE k.KullaniciAdi = {0} AND k.Sifre = {1}", kullaniciAdi, sifre)
                .FirstOrDefault();

            if (kullanici != null)
            {
                // Departman bilgisini ayrıca çekme
                var departman = _context.RolDepartman
                    .FirstOrDefault(d => d.RolDepartmanID == kullanici.RolDepartmanID);

                HttpContext.Session.SetInt32("KullaniciID", kullanici.KullaniciID);
                HttpContext.Session.SetInt32("RolDepartmanID", kullanici.RolDepartmanID);
                HttpContext.Session.SetString("RolDepartmanAdi", departman.RolDepartmanAdi);

                if (kullanici.KullaniciID == 1)
                {
                    return RedirectToAction("AdminCagrilar", "Cagrilar");
                }
                else
                {
                    return RedirectToAction("Cagrilar", "Cagrilar");
                }
            }

            ViewBag.Error = "Geçersiz kullanıcı adı veya şifre";
            return View("GirisEkrani");
        }
    }
}