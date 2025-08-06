using Demires.Data;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews();

// DbContext yap�land�rmas�
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

// Session yap�land�rmas�
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(20); // 20 dakika oturum s�resi
    options.Cookie.HttpOnly = true; // G�venlik i�in
    options.Cookie.IsEssential = true; // GDPR i�in gerekli
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

// Session middleware'ini ekliyoruz (UseRouting ve UseAuthorization aras�nda da olabilir)
app.UseSession();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=GirisEkrani}/{action=GirisEkrani}/{id?}");

app.Run();