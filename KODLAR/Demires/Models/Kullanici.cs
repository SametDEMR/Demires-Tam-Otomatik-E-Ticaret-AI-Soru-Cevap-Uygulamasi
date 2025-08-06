public class Kullanici
{
    public int KullaniciID { get; set; }
    public string KullaniciAdi { get; set; }
    public string Sifre { get; set; }
    public int RolDepartmanID { get; set; }
    public RolDepartman RolDepartmanAdi { get; set; }

}

public class RolDepartman
{
    public int RolDepartmanID { get; set; }
    public string RolDepartmanAdi { get; set; }
}
