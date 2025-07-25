# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 09:54:16 2024

@author: Vincent

Code to run and plot the SEIR model code 
"""

import scipy
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import seaborn as sns
from thesis_modules import *

### Plots
def per_capita_plot(axes,ts,x,CAR,N_vec_division,asymptote=None,per_x_pop = 100000,names="ethnic",colours=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],linesty='solid'):
    '''
    axes: pyplot axes to plot onto
    ts: 1D array of times to plot
    x: n by len(ts) array of values to plot (usually 4 here)'''

    if names == 'ethnic':
        names = ["Māori","Pacific","Asian","European/Other"]
    elif names == 'SEIR':
        names = ['Susceptible', 'Exposed', 'Infectious','Recovered']
    elif names == 'SSvEIR':
        names = ['Susceptible', 'Exposed', 'Infectious','Recovered']
    
    
    if isinstance(N_vec_division,(float,int,np.integer)):
        N_vec_division = np.full(len(names),N_vec_division)
    elif not isinstance(N_vec_division, list):
        N_vec_division = N_vec_division.flatten()
    
    axes.set_xlabel("Time (days)")
    
    
    if asymptote == 'Maori': # Adds asympotes for SEIR plots
        asymptote = return_attack_rates(CAR)[0]*per_x_pop / 100
    elif asymptote == 'Pacific':
        asymptote = return_attack_rates(CAR)[1]*per_x_pop / 100
    elif asymptote == 'Asian':
        asymptote = return_attack_rates(CAR)[2]*per_x_pop / 100
    elif asymptote == 'European':
        asymptote = return_attack_rates(CAR)[3]*per_x_pop / 100
    if not asymptote == None:
        axes.hlines(asymptote,0,max(ts),color =colours[3], linestyles='dashed')
    
    if isinstance(x, tuple) and len(x) == len(N_vec_division):
        
        for i in range(len(x)):
            axes.plot(ts,per_x_pop*x[i]/N_vec_division[i],linestyle=linesty,label=names[i],color=colours[i])
    elif np.shape(x)[0] == len(N_vec_division):
            for i in range(len(N_vec_division)):
                axes.plot(ts,per_x_pop*x[i,:]/N_vec_division[i],linestyle=linesty,label=names[i],color=colours[i])
    elif np.shape(x)[1] == len(N_vec_division):
            for i in range(len(N_vec_division)):
                axes.plot(ts,per_x_pop*x[:,i]/N_vec_division[i],linestyle=linesty,label=names[i],color=colours[i])
    else:
        print("N_vec and x have different dimentions, or x is not a matching tuple or array")
        
def heat_map(matrices,titles,scaling=0,create_fig=True,labels=["Māo","Pac","Asi","Oth"],max_comp='rowwise'):
    '''Can handle 1 heatplot or equal numbers of heatplots
    plots are plotted in order left to right, top to bottom (i.e. top row then bottom)
    If only two matrices are passed plot them side by side
    scaling is an int or list of len equal to the number of matrices, matrices get
    multiplied by 10**scaling'''
    
    if not (len(matrices) == 1 or not len(matrices)%2):
        print('Number of matrices must be 1 or even number')
    else:
        if isinstance(titles, str):
            titles = [titles]
        
        if create_fig:
            if isinstance(matrices, tuple):
                if len(matrices) == 2:
                    fig, axs = plt.subplots(1,2,figsize=(8,4),squeeze=False)
                    i_range=1
                else:
                    fig, axs = plt.subplots(2,len(matrices) // 2,figsize=(4*len(matrices)//2,8))
                    i_range=len(matrices)//2 # number of columns in plot
                
                # Scaled all matrices the same if a single scaling value is passed
                if isinstance(scaling,int):
                    scaling = [scaling] * len(matrices)
                        
                
                
                # Find max
                if max_comp=='rowwise': # finds max of rows seperately
                    curr_max=np.zeros(2)
                    for i in range(i_range):
                        curr_max[0]=max(curr_max[0],np.max(matrices[i]*10**scaling[i]))
                        curr_max[1]=max(curr_max[1],np.max(matrices[i+i_range]*10**scaling[i+i_range]))
                elif max_comp=='overall': # Finds max of all matrices
                    curr_max = 0
                    for i,matrix in enumerate(matrices):
                        curr_max = np.max(np.maximum(curr_max,matrix*10**scaling[i]))
                
                for i in range(i_range): # Iterate over all columns
                    for j in range(2): # iterate over rows
                        
                        if max_comp=='rowwise':
                            max_val = curr_max[j]
                        elif max_comp=='overall':
                            max_val = curr_max
                        else:
                            max_val = np.max(matrices[i+j*i_range])
                        
                        sns.heatmap(matrices[i+j*i_range]*10**scaling[i+j*i_range],
                                    annot=True, fmt=f'.{4}g', ax=axs[j,i],
                                    cmap="viridis", vmin=0, vmax=max_val,
                                    xticklabels=labels,yticklabels=labels,cbar=False,
                                    rasterized=True)
                        if scaling[i+j*i_range] == 0:
                            axs[j,i].set_title(f'{["a","b","c","d","e","f","g","h","i","j","k","l"][i+j*i_range]}) {titles[i+j*i_range]}')
                        else:
                            axs[j,i].set_title(f'{["a","b","c","d","e","f","g","h","i","j","k","l"][i+j*i_range]}) {titles[i+j*i_range]} (10$^{{-{scaling[i+j*i_range]}}}$)')
        
            else: # Handle single heat_maps
                fig, axs = plt.subplots(1,1,figsize=(4,4))
                if isinstance(scaling,tuple) or isinstance(scaling,list): # extract first element of list or tuple
                    scaling = scaling[0]
                
                # Plot
                sns.heatmap(matrices*10**scaling, annot=True, fmt=f'.{4}g', ax=axs,
                            cmap="viridis", vmin=0, vmax=np.max(matrices),
                            xticklabels=labels,yticklabels=labels,cbar=False,
                            rasterized=True)
                
                if isinstance(titles,tuple) or isinstance(titles,list): # extract first element of list or tuple
                    titles = titles[0]
                if scaling == 0:
                    axs.set_title(f'{titles}')
                else:
                    axs.set_title(f'{titles} (10$^{{-{scaling}}}$)')
        
def barplot(axes,bar_groups,y_title,x_title = 'CAR (%)',labels='ethnic',x_ticks = 'CAR',has_legend=True,is_big_text=False,
            is_maroon=False):
    '''bar_groups: a tuple or list of groups of barcharts
    y_title: title of y-axis
    labels: labels for each bar in bar group
    is_big_text: increase size of text, but disables legend'''
    
    if labels == 'ethnic':
        labels = ['Māori',"Pacific Peoples","Asian","European/Other"]
    
    if x_ticks == 'CAR':
        x_ticks = ['40/60','40','50','60']
    elif x_ticks == 'SA':
        x_ticks = ['SA1 total', 'SA2 total','SA2 prioritised']
    
    if (not isinstance(bar_groups,list)) and not isinstance(bar_groups,tuple):
        bar_groups = [bar_groups]
    
    filename = 'barplot_contact_vector'
    # creating the bar plot
    if is_big_text:
        matplotlib.rcParams.update({'font.size': 14})
    if is_maroon and len(bar_groups)==1:
        a = bar_groups[0]
        r = np.arange(len(bar_groups[0]))
        bar_width = 0.8
        axes.bar(r, a[:,0],
                width=bar_width,label='Data', color='maroon')
        axes.set_ylabel(y_title)
        axes.set_xticks(r)
        axes.set_xticklabels(x_ticks)
        axes.set_ylim(1,max(a)*1.01)
        axes.set_xlabel(x_title)
        # save_image(filename,is_prop,CAR,is_statsnz, is_SA1, is_non_parametric, is_vacc,counter_factual_scen,file_format='png')
    else:
        filename = 'barplot_contact_vector_comp'
        
        bars = np.zeros([len(bar_groups[0]),len(bar_groups)])
        
        for i,bar_group in enumerate(bar_groups):
            bars[:,i] = bar_group.flatten()
        
        # if len(bar_groups) == 1:
        #     r = np.arange(len(bar_groups[0]))
        # else:
        r = np.arange(len(bar_groups))
            
        bar_width = 0.8 / len(bar_groups[0])
        
        for i in range(len(bar_groups[0])):
            axes.bar(r+bar_width*i, bars[i,:], label=labels[i],
                width=bar_width)
        if has_legend and not is_big_text:
            axes.legend()
        axes.set_ylim(0,np.max(bars)*1.05)
        if len(r) == len(x_ticks):
            axes.set_xticks(r+1.5*bar_width)
            axes.set_xticklabels(x_ticks)
            
        axes.set_ylabel(y_title)
        axes.set_xlabel(x_title)
    # if is_compare_SA and (not is_statsnz) and (not is_prop):
    #     filename = 'barplot_contact_vector_SAcomp'
    #     epsilon1, aSA1 = epsilon_a_vector(CAR,True,True,is_vacc,is_prop,
    #                             is_non_parametric,is_old = False)
    #     epsilon1, aSA2t = epsilon_a_vector(CAR,False,True,is_vacc,is_prop,
    #                       is_non_parametric,is_old = False)
    #     epsilon1, aSA2p = epsilon_a_vector(CAR,False,False,is_vacc,is_prop,
    #                               is_non_parametric,is_old = False)

    #     a_mao = [aSA1[0,0],aSA2t[0,0],aSA2p[0,0]]
    #     a_pac = [aSA1[1,0],aSA2t[1,0],aSA2p[1,0]]
    #     a_asi = [aSA1[2,0],aSA2t[2,0],aSA2p[2,0]]
    #     a_oth = [aSA1[3,0],aSA2t[3,0],aSA2p[3,0]]
    #     fig, ax = plt.subplots()
    #     r = np.arange(3)
    #     bar_width = 0.2
    #     ax.bar(r, a_mao, label="Māori",
    #             width=bar_width, color='tab:blue')
    #     ax.bar(r+ bar_width, a_pac, label = "Pacific Peoples",
    #             width=bar_width, color='tab:orange')
    #     ax.bar(r + 2*bar_width, a_asi, label="Asian",
    #             width=bar_width, color='tab:green')
    #     ax.bar(r+ 3*bar_width, a_oth, label = "European/Other",
    #             width=bar_width, color='tab:red')
    #     ax.legend()
    #     plt.ylim(0,np.max([aSA1,aSA2t,aSA2p])+0.05)
    #     ax.set_xticks(r+1.5*bar_width)
    #     ax.set_xticklabels(['SA1 total','SA2 total','SA2 priority'])
    #     ax.set_ylabel("Contact rate (per day)")
    #     save_image(filename,is_prop,CAR,is_statsnz, is_SA1, is_non_parametric, is_vacc,counter_factual_scen)
    #     plt.show()
    
    if is_big_text:
        matplotlib.rcParams.update({'font.size': 10})
    




def SEIR_plot(N_vec,CAR,is_vacc,is_prop,is_non_parametric,is_SA1,is_statsnz,counterfactual):
    ### Prop mix SEIR
    is_per_capita = True
    plt.rcParams.update({'font.size': 14})
    plt.rcParams.update({'legend.fontsize':10})
    ts, S,Sv, E, I, R, In = load_SEIR_results(CAR,is_vacc,is_prop,is_non_parametric,
                      counterfactual = -1, is_SA1=is_SA1,is_statsnz=is_statsnz)
    fig, ax = plt.subplots(2,2,figsize=(6.8*2,4.8*2))
    attack_rates = return_attack_rates(CAR)
    for i in range(2):
        for j in range(2):
            ax[j,i].set_xlabel('Time (Days)')
            if is_per_capita:
                per_capita_plot(ax[j,i],ts,np.array([S[2*j+i]+Sv[2*j+i],E[2*j+i],I[2*j+i],R[2*j+i]]), CAR,
                                N_vec[2*j+i,0],asymptote=['Maori','Pacific','Asian','European'][2*j+i],
                                per_x_pop = 100000,names="ethnic")
                ax[j,i].set_xlim(0,max(ts))
                ax[j,i].set_ylabel('Population (per 100k)')
            else:
                per_capita_plot(ax[j,i],ts,np.array([S[2*j+i]+Sv[2*j+i],E[2*j+i],I[2*j+i],R[2*j+i]]),CAR,np.array([[1,1,1,1]]).T,names="SEIR",per_x_pop=1/100000)
                ax[j,i].axhline(attack_rates[2*j+i]*N_vec[2*j+i,0]/10000000,color='tab:red',linestyle='dashed')
                ax[j,i].set_xlim(0,max(ts))
                ax[j,i].set_ylabel('Population (100k)')
    ax[0,1].legend()
    ax[0,0].set_title('a) Māori')
    ax[0,1].set_title('b) Pacifc')
    ax[1,0].set_title('c) Asian')
    ax[1,1].set_title('d) European/Other')
    fig.tight_layout()
    plt.rcParams.update({'font.size': 10})
    plt.rcParams.update({'legend.fontsize':10})


# ### Contact rate and reproduction number
def contact_vs_reproduction_number(N_vec, N_vec_vacc,is_SA1,is_statsnz,
                                   is_vacc,is_prop,is_non_parametric, gamma):
    plt.rcParams.update({'font.size': 14})
    plt.rcParams.update({'legend.fontsize':10})
    fig,ax = plt.subplots(1,2,figsize=(6.8*2,4.8)) 
    
    # Grab contact rates and their reproduction number
    a_vectors = []
    reprod_numbers = []
    for CAR_val in ['4060',40,50,60]:
        epsilon1, a1 = epsilon_a_vector(CAR_val,is_SA1,is_statsnz,is_vacc,is_prop,
                  is_non_parametric,is_old = False)
        a_vectors.append(a1)
        
        reprod_numbers.append(initial_reproduction_number(N_vec, N_vec_vacc,CAR_val,is_SA1,is_statsnz,is_vacc,is_prop,is_non_parametric, gamma))
    
    # Plot transmission rates
    barplot(ax[0],a_vectors,"Transmission rate (per day)")
    
    
    # Plot reproduction number
    barplot(ax[1],np.array([reprod_numbers]).T,
            "Initial reproduction number",is_maroon=True, x_ticks='CAR')
    ax[1].set_title('b) Initial reproduction numbers')
    ax[0].set_title('a) Transmission rates')
    ax[1].tick_params(labelsize=10)
    
    ax[0].tick_params(labelsize=10)
    plt.rcParams.update({'font.size': 10})
    plt.rcParams.update({'legend.fontsize':10})


def contact_vs_contact_rates(N_vec, N_vec_vacc,is_SA1s,is_statsnzs,
                                   is_vacc,is_props,is_non_parametrics, titles=None):
    '''is_SA1s, is_statsnz, is_props, is_non_parametrics all must be tuples or lists'''
    
    plt.rcParams.update({'font.size': 14})
    plt.rcParams.update({'legend.fontsize':10})
    fig,ax = plt.subplots(1,len(is_SA1s),figsize=(6.8*2,4.8)) 
    
    # Grab contact rates and their reproduction number
    a_vectors = np.zeros([len(is_SA1s),4,4])
    for i in range(len(is_SA1s)):
        for j, CAR_val in enumerate(['4060',40,50,60]):
            epsilon1, a1 = epsilon_a_vector(CAR_val,is_SA1s[i],is_statsnzs[i],is_vacc,is_props[i],
                      is_non_parametrics[i],is_old = False)
            a_vectors[i,j,:] = a1.flatten()
    
    if titles is None:
        titles = ['']*len(is_SA1s)
    
    # Plot transmission rates
    for i in range(len(is_SA1s)):
        curr_list = []
        # Convert a_vectors to lists
        for j in range(4):
            curr_list.append(a_vectors[i,j,:])
            
        
        barplot(ax[i],curr_list,"Transmission rate (per day)")
    
        ax[i].set_title(f'{["a","b","c","d"][i]}) {titles[i]} transmission rates')
        ax[i].tick_params(labelsize=10)
        
        # Make all axes the same scale
        ax[i].set_ylim(0,np.max(a_vectors)*1.05)
        # Remove legend from all but final
        if i < (len(is_SA1s)-1):
            ax[i].get_legend().remove()
    plt.rcParams.update({'font.size': 10})
    plt.rcParams.update({'legend.fontsize':10})



def quantification_plot(N_vec,CAR, is_SA1, is_statsnz):
    # ### Quantification
    # -1 is no scenario, 0 is equal vaccine, 1 is no vaccines, 2 is SEIRS model
    # 3 is no assortativity
    # 4 is setting all contact rates to weighted average contact rate
    # 5 is setting all vaccination rates to weighted average vaccine rate
    is_prop  = False
    is_non_parametric = False
    is_vacc = True
    
    ts, S,Sv, E, I, R, In = load_SEIR_results(CAR,is_vacc,is_prop,is_non_parametric,
                      counterfactual = -1, is_SA1=is_SA1,is_statsnz=is_statsnz)
    In1 = 100*In[:,-1] / N_vec.flatten()
    ts, S,Sv, E, I, R, In = load_SEIR_results(CAR,is_vacc,is_prop,is_non_parametric,
                      counterfactual = 3, is_SA1=is_SA1,is_statsnz=is_statsnz)
    In2 = 100*In[:,-1] / N_vec.flatten()
    ts, S,Sv, E, I, R, In = load_SEIR_results(CAR,is_vacc,is_prop,is_non_parametric,
                      counterfactual = 5, is_SA1=is_SA1,is_statsnz=is_statsnz)
    In3 = 100*In[:,-1] / N_vec.flatten()
    ts, S,Sv, E, I, R, In = load_SEIR_results(CAR,is_vacc,is_prop,is_non_parametric,
                      counterfactual = 4, is_SA1=is_SA1,is_statsnz=is_statsnz)
    In4 = 100*In[:,-1] / N_vec.flatten()
    fig,ax = plt.subplots()
    barplot(ax,[In1,In2,In3,In4],"Attack rate",x_ticks=['1','2','3','4'],x_title='Scenario')
    ### lines - muddy the plot so are commented out
    # ax.axhline(In1[0],linestyle='dashed')
    # ax.axhline(In1[1],linestyle='dashed',color='tab:orange')
    # ax.axhline(In1[2],linestyle='dashed',color='tab:green')
    # ax.axhline(In1[3],linestyle='dashed',color='tab:red')

def model_simulation_epsilon_var(a0, CAR, SEIR_0, N_vec, time, sigma,gamma, epsilon):
    '''Acts as a loss function for fitting a contact rate to a value of
    assortativity.
    Takes as an input a contact vector (of floats). Also uses a global float 
    variable, epsilon, as an assortativity value.
    It then runs an SEIR model and determines the difference between some
    specified global variable attack rates (mao_N2,pac_N2,asi_N2,oth_N2)
    the absolute values of these differences is added and returned'''
    # Conver a to a column vector
    a0.flatten()
    a0=np.array([a0]).T 
    
    # beta is the transmission matrix
    beta = (1-epsilon)*(a0 @ a0.T)/(a0.T @ N_vec) + epsilon * np.diag(a0[:,0] / N_vec[:,0])
    
    
    solution = scipy.integrate.solve_ivp(SEIR_model,[0,time],SEIR_0, args=(beta,sigma,gamma))
    
    attack_rates = return_attack_rates(CAR)
    
    attack_rate_diff = attack_rates.flatten() - 100 * (N_vec.flatten() - (solution.y[0:4,-1]+solution.y[4:8,-1])) / N_vec.flatten()
    
    
    return attack_rate_diff


def epsilon_variation_plot(CAR,N_vec,is_vacc,N_vec_vacc, time, sigma,gamma,is_save_generated_plots,res=31):
    '''Returns a 1x2 subplot of variation of peak position and variation
    of attack rate.
    
    Variation of peak position fits a new set of transmission rates to each
    value of epsilon and runs an SEIR model to find the day of the peak daily
    infections for each ethnicity and plots that for 0<epsilon<1
    
    Variation of attack rate takes the proportionate mixing fit and varies
    epsilon, each time recalculating the attack rate of the model, which
    is then plotted for each ethnicity
    '''
    # Grab proportionate mixing transmission rate and initial condition for SEIR model run
    epsilon, a_prop = epsilon_a_vector(CAR,is_SA1=None,is_statsnz=None,is_vacc=is_vacc,
                              is_prop=True,is_non_parametric=False)
    SEIR_0 = np.concatenate(initial_group_populations(N_vec,is_vacc,N_vec_vacc))
    ### Storage Vectors
    peak_idxs = np.zeros([4,res])
    model_attack_rates = np.zeros([4,res])
    
    for j in range(res):
        
        ### Values to iterate over
        epsilons = np.linspace(0,1,res)
        
        ### Transmission mattrix
        # a is the ethnicity contact rate, i.e. How often an ethnicity contacts others
    
        # Definie initial starting popint for fitting 
        a = np.array([[0.5,0.5,0.18,0.18]]).T
        
        # Grab new value for assortativity
        epsilon  = epsilons[j] 
        
        # Fit transmission rate
        result = scipy.optimize.fsolve(model_simulation_epsilon_var,a.flatten(),
                                       args=(CAR, SEIR_0, N_vec, time, sigma,gamma, epsilon))
        a = np.array([result]).T
        
        # using new value of a to run SEIR model
        beta = (1-epsilon)*(a @ a.T)/(a.T @ N_vec) + epsilon * np.diag(a[:,0] / N_vec[:,0])
        solution_SEIR = scipy.integrate.solve_ivp(SEIR_model,[0,time],SEIR_0,t_eval=np.arange(0,time+1),
                                                  args=(beta, sigma, gamma))
        
        # From SEIR model result, extract peak daily infections for each ethnicity
        peak_idxs[:,j] = np.argmax(solution_SEIR.y[8:12],axis=1)
        
        
        ### Handle attack rate variation
        beta = (1-epsilon)*(a_prop @ a_prop.T)/(a_prop.T @ N_vec) + epsilon * np.diag(a_prop[:,0] / N_vec[:,0])
        solution = scipy.integrate.solve_ivp(SEIR_model,[0,time],SEIR_0,
                                             args=(beta,sigma,gamma))
        
        # extract attack rates from model run and store them
        model_attack_rates[:,j] = 100 * (N_vec.flatten() - (solution.y[0:4,-1]+solution.y[4:8,-1])) / N_vec.flatten()
        
        if not j%5:
            print(f'parameter variation: {j+1} / {res}')
        
    ### plotting contact vector variation
    fig,axs = plt.subplots(1,2,figsize=(14,4.8))
    axs[0].plot(epsilons,peak_idxs[0,:],label="Maori")
    axs[0].plot(epsilons,peak_idxs[1,:],label="Pacific Peoples")
    axs[0].plot(epsilons,peak_idxs[2,:],label="Asian")
    axs[0].plot(epsilons,peak_idxs[3,:],label="European/Other")
    axs[0].legend()
    axs[0].set_xlabel("Epsilon")
    axs[0].set_ylabel("Peak position (Days since start of simulation)")
    axs[0].set_title("a) Variation of peak position")
    axs[0].set_xlim(0,1)
    
    # ### Attack rate variation
    axs[1].plot(epsilons,model_attack_rates[0,:],label="Maori")
    axs[1].plot(epsilons,model_attack_rates[1,:],label="Pacific Peoples")
    axs[1].plot(epsilons,model_attack_rates[2,:],label="Asian")
    axs[1].plot(epsilons,model_attack_rates[3,:],label="European/Other")
    axs[1].legend()
    axs[1].set_xlabel("Epsilon")
    axs[1].set_ylabel('Attack rate (%)')
    axs[1].set_ylim(0,100)
    axs[1].set_xlim(0,1)
    axs[1].set_title("b) Variation of attack rate")
    plt.tight_layout()
    
    if is_vacc:
        is_vacc_str = ''
        filename = f'vaccine_epsilon_variation_CAR{CAR}.pdf'
        file_location = f"../Images/Vaccine_analysis/"
    else:
        is_vacc_str = ''
        filename = f'epsilon_variation_CAR{CAR}.pdf'
        file_location = f"../Images/"
    
    if is_save_generated_plots:
        plt.savefig(f'{file_location}{filename}',dpi=300)
        print(f'Saved as {filename} at {file_location}')
