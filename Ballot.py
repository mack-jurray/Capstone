#from web3.auto import w3
from web3 import Web3
from phe import paillier
import importlib
import time
import subprocess
import datetime
import random


w3 = Web3(Web3.IPCProvider('~/gethDataDir/geth.ipc'))
##print(w3.isConnected())
w3.geth.personal.unlockAccount(w3.geth.personal.listAccounts()[2],"test123", 15000)
w3.geth.personal.unlockAccount(w3.eth.coinbase,"test1", 15000)

def split_mes(mes):
    emb = 20
    #pad message
    if len(mes) % 20 != 0:
        mes = mes + 'a' * (emb - len(mes) % emb)
    a = [mes[i:i+20] for i in range(0,len(mes),20)]
    return a

def send_mes(mes):
    toAddr = w3.geth.personal.listAccounts()[2]
    toAddr = "0xbb9a57ce2309bf5f27633ba1efd48f291e963e1b"
    toAddr = w3.toChecksumAddress(toAddr)
    byteMes = bytes(mes,'utf-8')
    a = w3.eth.sendTransaction({'to': toAddr, 'from': w3.eth.coinbase, 'value': 12345678, 'data': byteMes})
    print(a)
    w3.geth.miner.start(1)
    time.sleep(.3)
    w3.geth.miner.stop()


if __name__ == "__main__":
    # Run the Ballot System
    public_key, private_key = paillier.generate_paillier_keypair()

    # Initialized with 2 Candidates
    # Do not keep count of votes since it is stored on the network
    candidates = ["Candidate 1", "Candidate 2"]
    # We create a dictionary with candidates and vote tallies
    candidateVotes = {"Candidate 1":0,"Candidate 2":0}
    # Grabs the oldest/most recent block number
    block_old = w3.eth.get_block('latest').number
    results_checked = 0

    while(1):
        print("Welcome to the CLJ Election System")
        print("Please select a number:")
        print("\t(1) Vote")
        print("\t(2) Results")
        print("\t(3) About")
        numberInput = input()

        if numberInput == "1":
            results_checked = 1
            # Ballot
            print("Who Would You Like to Vote For? Please select a number")
            for i in range(1,len(candidates)+1):
                print("\t("+ str(i) + ") " + candidates[i-1])
            print("\t("+ str(len(candidates)+1)+ ") Add a Candidate")
            canInput = int(input())-1
            print("")

            if (canInput < len(candidates)) and (int(canInput) >= 0):
                candidateName = candidates[int(canInput)]
                # Encrypt in the dictionary
                # Adds a vote to the number of votes for the candidate
                encryptedVotes = public_key.encrypt(int(candidateVotes[candidateName])+1)
                encryptedVotes = encryptedVotes.ciphertext()

                # Send it to the Ethereum network
                # Update the votes for the candidates
                send_mes(candidateName+"-"+str(encryptedVotes))

                # If this were LIVE, it would only allow 1 vote per message sent
                # print("Thank you for voting! Have a great day!")
                # exit()

            if canInput == len(candidates):
                nameNew = input("Type in the name of the new candidate: ")
                print("")
                candidateVotes[nameNew] = 0
                candidates.append(nameNew)
                # Encrypt in the dictionary
                # Adds a vote to the number of votes for the candidate
                encryptedVotes = public_key.encrypt(int(candidateVotes[nameNew])+1)
                encryptedVotes = encryptedVotes.ciphertext()

                # Send it to the Ethereum network
                # Update the votes for the candidates
                send_mes(nameNew+"-"+str(encryptedVotes))

            if (int(canInput) > len(candidates)) or (int(canInput) < 0):
                print("You entered an incorrect number. Please try again.")
                print("")
                exit()

        # Results for the votes of each candidate
        if numberInput == "2":
            if results_checked == 0:
                print("Election Results")
                print("Name\t\tVote Tally")
                for can in candidateVotes:
                    print(can+"\t\t"+str(candidateVotes[can]))
                print("")
            else:
                results_checked = 1
                # Use old block and iterate to the newest
                newBlock = w3.eth.get_block('latest').number

                for block_old in range(block_old, newBlock):
                    tempBlockTransaction = w3.eth.get_block(block_old).transactions
                    if len(tempBlockTransaction) != 0:
                        currentTrans = w3.eth.get_transaction(tempBlockTransaction[0])
                        data = currentTrans.input

                # Decrypt the data
                new_data = bytes.fromhex(data[2:]).decode('utf-8')

                # Updated the dictionary
                listDataUpdate = new_data.split('-')
                can_name = listDataUpdate[0]
                encrypt_vote = int(listDataUpdate[1])

                decrypt_vote = private_key.raw_decrypt(encrypt_vote)
                candidateVotes[can_name] = decrypt_vote
                print("Election Results")
                print("Name\t\tVote Tally")
                for can in candidateVotes:
                    print(can+"\t\t"+str(candidateVotes[can]))
                print("")

        if numberInput == "3":
            print("Program By:\t\tMIDN 1/C Chase Lee, Luke Harkins, Jack Murray")
            print("Acknowledgements:\tLT Vikram Kanth, Professor Travis Mayberry")
            print("")
            print("")
