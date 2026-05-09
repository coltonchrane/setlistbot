using System.Net.Http.Headers;
using System.Text.Json;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddOpenApi();
builder.Services.AddHttpClient("MusicBrainz", client =>
{
    client.BaseAddress = new Uri("https://musicbrainz.org/ws/2/");
    client.DefaultRequestHeaders.UserAgent.ParseAdd("SetlistBotApi/1.0.0 (https://github.com/coltonchrane/setlistbot)");
    client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
});
builder.Services.AddHttpClient("SetlistFm", client =>
{
    client.BaseAddress = new Uri("https://api.setlist.fm/rest/1.0/");
    client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseHttpsRedirection();

app.MapGet("/api/setlist", async (string artist, string? date, IHttpClientFactory clientFactory, IConfiguration config) =>
{
    var apiKey = config["SETLIST_FM_API_KEY"] ?? config["apikey"];
    if (string.IsNullOrEmpty(apiKey))
    {
        return Results.Problem("Setlist.fm API Key is missing.");
    }

    var mbClient = clientFactory.CreateClient("MusicBrainz");
    var sfmClient = clientFactory.CreateClient("SetlistFm");
    sfmClient.DefaultRequestHeaders.Add("x-api-key", apiKey);

    try
    {
        // 1. Search MusicBrainz for Artist MBID
        var mbResponse = await mbClient.GetAsync($"artist/?query=artist:{Uri.EscapeDataString(artist)}&fmt=json");
        if (!mbResponse.IsSuccessStatusCode) return Results.Problem("Failed to search MusicBrainz");
        
        var mbContent = await mbResponse.Content.ReadAsStringAsync();
        using var mbDoc = JsonDocument.Parse(mbContent);
        var artistNode = mbDoc.RootElement.GetProperty("artists")[0];
        var mbid = artistNode.GetProperty("id").GetString();
        var resolvedArtistName = artistNode.GetProperty("name").GetString();

        // 2. Fetch Setlist from Setlist.fm
        var sfmUrl = $"search/setlists?artistMbid={mbid}&p=1";
        if (!string.IsNullOrEmpty(date)) sfmUrl += $"&date={date}";

        var sfmResponse = await sfmClient.GetAsync(sfmUrl);
        if (sfmResponse.StatusCode == System.Net.HttpStatusCode.NotFound)
        {
            return Results.NotFound(new { message = "No show record for that date" });
        }
        if (!sfmResponse.IsSuccessStatusCode) return Results.Problem("Failed to fetch setlist from Setlist.fm");

        var sfmContent = await sfmResponse.Content.ReadAsStringAsync();
        
        // Return raw for now, or we can map it to a clean DTO
        return Results.Content(sfmContent, "application/json");
    }
    catch (Exception ex)
    {
        return Results.Problem(ex.Message);
    }
})
.WithName("GetSetlist");

app.Run();
