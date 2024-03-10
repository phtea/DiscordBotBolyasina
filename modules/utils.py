# Extend the send method of ctx to support chunking
async def chunked_send(ctx, message):
    chunks = [message[i:i + 2000] for i in range(0, len(message), 2000)]
    for chunk in chunks:
        await ctx.send(chunk)