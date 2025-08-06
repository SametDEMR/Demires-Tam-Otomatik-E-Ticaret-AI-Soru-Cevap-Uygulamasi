using Demires.Models;
using Microsoft.EntityFrameworkCore;

namespace Demires.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        public DbSet<Kullanici> Kullanici { get; set; }
        public DbSet<RolDepartman> RolDepartman { get; set; }
        public DbSet<Cagrilar> Cagrilar { get; set; }
    }
}