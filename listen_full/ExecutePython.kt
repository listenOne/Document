package function

import java.io.BufferedReader
import java.io.InputStreamReader

object ExecutePython {

    @JvmStatic
    fun main(args: Array<String>) {

        val pythonFilePath = "D:\\catface\\IDEA\\Python\\src\\listen_full\\qq\\api_qq.py"

        val process = Runtime.getRuntime().exec("python $pythonFilePath")

        val reader = BufferedReader(InputStreamReader(process.inputStream))

        var line: String?

        while (true) {
            line = reader.readLine() ?: break
            println(line)
        }

        reader.close()

        process.waitFor()

        println("execute completed....")
    }
}