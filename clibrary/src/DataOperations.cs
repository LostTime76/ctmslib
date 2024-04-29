using CeetemSoft.Utils;
using System.Runtime.InteropServices;

unsafe internal static class DataOperations
{
	[UnmanagedCallersOnly(EntryPoint = "rev16")]
	internal static void Rev16(byte* data, int dlen)
	{
		DataUtils.Rev16(new Span<byte>(data, dlen));
	}

	[UnmanagedCallersOnly(EntryPoint = "crc32")]
	public static uint Crc32(byte* data, int dlen)
	{
		return System.IO.Hashing.Crc32.HashToUInt32(new ReadOnlySpan<byte>(data, dlen));
	}
}