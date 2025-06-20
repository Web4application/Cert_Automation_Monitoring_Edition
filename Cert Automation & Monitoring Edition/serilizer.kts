package ai.projectpilot.logging

import com.google.gson.JsonElement
import com.google.gson.JsonObject
import com.google.gson.JsonSerializationContext
import com.google.gson.JsonSerializer
import org.assertj.swing.exception.ComponentLookupException
import java.lang.reflect.Type
import java.time.Instant
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

class ComponentLookupExceptionSerializer : JsonSerializer<ComponentLookupException> {
    override fun serialize(
        src: ComponentLookupException,
        typeOfSrc: Type,
        context: JsonSerializationContext
    ): JsonElement {
        val json = JsonObject()
        json.addProperty("type", "ComponentLookupException")
        json.addProperty("timestamp", DateTimeFormatter.ISO_INSTANT.format(Instant.now().atOffset(ZoneOffset.UTC)))
        json.addProperty("message", src.message ?: "No message provided")
        json.addProperty("suggestedFix", suggestFix(src.message))
        return json
    }

    private fun suggestFix(message: String?): String {
        return when {
            message == null -> "Review the component locator logic."
            message.contains("name", ignoreCase = true) -> "Ensure the component name is correct and visible in the UI."
            message.contains("index", ignoreCase = true) -> "Check if the index used is within bounds of rendered components."
            else -> "Verify component visibility and matching criteria in your test."
        }
    }
}
