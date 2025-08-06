using System.ComponentModel.DataAnnotations;

namespace Demires.Models
{
    public class Cagrilar
    {
        [Key]
        public int CagriID { get; set; }
        public string Konu { get; set; }
        public int MusteriID { get; set; }
        public int? CevaplayanID { get; set; }
        public int DepartmanID { get; set; }
        public int Durum { get; set; }
        public string Mesaj { get; set; }
    }
}