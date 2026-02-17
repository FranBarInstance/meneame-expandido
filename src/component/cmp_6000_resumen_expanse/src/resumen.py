"""Parse Feed and Generate AI Summary."""

import re
from urllib.error import HTTPError
from ai_backend_0yt2sa import AIManager

import fastfeedparser


def main(params=None):
    """Main function for Neutral TS callback."""

    resumen_url = params.get("resumen_url")
    resumen_name = params.get("resumen_name")
    resumen_valid_names = params.get("resumen_valid_names")
    prompt = params.get("prompt", "Haz un resumen")
    profile = params.get("profile", "ollama_local")

    return {
        "data": get_resumen(resumen_url, resumen_name, resumen_valid_names, prompt, profile)
    }


def get_resumen(resumen_url, resumen_name, resumen_valid_names, prompt, profile) -> dict:
    """Get RSS feed and generate AI summary."""
    schema_data = {'resumen_feed_error': ''}

    if not resumen_url:
        schema_data['resumen_feed_error'] = "No URL provided"
    elif not resumen_name:
        schema_data['resumen_feed_error'] = "No site name provided"
    elif resumen_name not in resumen_valid_names:
        schema_data['resumen_feed_error'] = "Invalid site name"
    else:
        try:
            # Parse the RSS feed
            feed = fastfeedparser.parse(resumen_url)
            if not feed.feed and not feed.entries:
                schema_data['resumen_feed_error'] = "No feed or entries found"
            else:
                schema_data['resumen_feed_url'] = resumen_url
                schema_data['resumen_feed_feed'] = feed.feed or {}
                schema_data['resumen_feed_entries'] = feed.entries or []

                # Build content for AI summary
                content = build_content_for_ai(feed, resumen_url)

                # Generate AI summary
                try:
                    ai_manager = AIManager()
                    full_prompt = f"{prompt}\n\n{content}"
                    ai_summary = ai_manager.prompt(profile, full_prompt)
                    schema_data['resumen_ai_summary'] = ai_summary
                except ValueError as e:
                    schema_data['resumen_feed_error'] = f"Error generating summary: {str(e)}"
                except ImportError as e:
                    schema_data['resumen_feed_error'] = f"AI backend not available: {str(e)}"
                except Exception as e:  # pylint: disable=broad-except
                    schema_data['resumen_feed_error'] = f"Error generating summary: {str(e)}"

        except HTTPError as e:
            schema_data['resumen_feed_error'] = str(e.reason)
        except (ImportError, Exception) as e:  # pylint: disable=broad-except
            schema_data['resumen_feed_error'] = str(e)

    schema_data['resumen_name'] = resumen_name

    return schema_data


def build_content_for_ai(feed, url) -> str:
    """Build content string from feed entries for AI processing."""
    content_parts = [f"URL del feed: {url}\n"]

    if feed.feed:
        feed_title = getattr(feed.feed, 'title', 'Sin título')
        feed_description = getattr(feed.feed, 'description', '')
        content_parts.append(f"Título del feed: {feed_title}")
        if feed_description:
            content_parts.append(f"Descripción: {feed_description}")
        content_parts.append("\n--- Entradas ---\n")

    # Limit entries to avoid token limits
    max_entries = 20
    for i, entry in enumerate(feed.entries[:max_entries]):
        entry_title = getattr(entry, 'title', 'Sin título')
        entry_summary = getattr(entry, 'summary', getattr(entry, 'description', ''))
        entry_link = getattr(entry, 'link', '')

        content_parts.append(f"\nEntrada {i + 1}:")
        content_parts.append(f"Título: {entry_title}")
        if entry_summary:
            # Clean HTML tags from summary
            clean_summary = re.sub(r'<[^>]+>', '', entry_summary)
            # Limit summary length
            if len(clean_summary) > 500:
                clean_summary = clean_summary[:500] + "..."
            content_parts.append(f"Resumen: {clean_summary}")
        if entry_link:
            content_parts.append(f"Enlace: {entry_link}")

    if len(feed.entries) > max_entries:
        content_parts.append(f"\n... y {len(feed.entries) - max_entries} entradas más.")

    return "\n".join(content_parts)
