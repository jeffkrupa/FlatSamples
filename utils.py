import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib 
import matplotlib.pylab as plt
from sklearn.metrics import auc
import mplhep as hep
import scipy
#hep.style.use("CMS")
from matplotlib import rcParams
plt.style.use([hep.style.ROOT, hep.style.firamath])
#plt.rcParams['text.usetex'] = True

plt.rc('xtick', labelsize=10)
plt.rc('ytick', labelsize=10)
plt.rc('axes', labelsize=12)
plt.rc('axes', titlesize=12)
plt.rc('legend', fontsize=10)
rlabel = "2017 (13 TeV)"
inlay_font = {
        'fontfamily' : 'arial',
        'weight' : 'normal',
        'size'   : 14
}
axis_font = {
        #'fontfamily' : 'arial',
        #'weight' : 'normal',
        'size'   : 24
}
legend_font = {
        #'family' : 'sans-serif',
        #'weight' : 'normal',
        'size'   : 16
}


nbins = 20
_titles={
  "zpr_fj_msd" : {"name" : "Jet $\mathrm{m_{SD}}$ (GeV)", "bins" : np.linspace(30,350,nbins)},
  "zpr_fj_pt"  : {"name" : "Jet $\mathrm{p_T}$ (GeV)",    "bins" : np.linspace(200,1500,nbins)},
  "zpr_fj_eta" : {"name" : "Jet $\mathrm{\eta}$",         "bins" : np.linspace(-3,3,nbins)},
  "zpr_fj_phi" : {"name" : "Jet $\mathrm{\phi}$",         "bins" : np.linspace(-np.pi,np.pi,nbins)},
  "zpr_fj_n2b1" : {"name" : "Jet $\mathrm{N_2}$",         "bins" : np.linspace(0,0.5,nbins)},
  "zpr_fj_tau21" : {"name" : "Jet $\mathrm{\tau_{2,1}}$", "bins" : np.linspace(0,1.0,nbins)},
  "zpr_genAK8Jet_eta" : {"name" : "Generator jet $\mathrm{\eta}$",  "bins" : np.linspace(-3,3,nbins)},
  "zpr_genAK8Jet_phi" : {"name" : "Generator jet $\mathrm{\phi}$",  "bins" : np.linspace(-np.pi,np.pi,nbins)},
  "zpr_genAK8Jet_partonFlavour" : {"name" : "Generator jet parton flavor",  "bins" : nbins},
  "zpr_genAK8Jet_hadronFlavour" : {"name" : "Generator jet hadron flavor",  "bins" : nbins},
  "zpr_genAK8Jet_mass" : {"name" : "Generator jet mass (GeV)",  "bins" : np.linspace(30,250,nbins)},
  "zpr_genAK8Jet_pt"   : {"name" : "Generator jet $\mathrm{p_T}$ (GeV)", "bins" : np.linspace(200,1500,nbins)},
  "zpr_fj_nparts"      : {"name" : "Number of particles", "bins" : np.linspace(0,150,51)},
  "zpr_fj_nBHadrons"   : {"name" : "Number of B hadrons", "bins" : np.linspace(0,10,11)},
  "zpr_fj_nCHadrons"   : {"name" : "Number of C hadrons", "bins" : np.linspace(0,10,11)},

  "zpr_PF_ptrel" :  {"name" : "Particle relative $\mathrm{p_T}$",  "bins" : np.linspace(0,1,nbins)},
  "zpr_PF_etarel" : {"name" : "Particle relative $\mathrm{\eta}$", "bins" : np.linspace(-1,1,nbins)},
  "zpr_PF_phirel" : {"name" : "Particle relative $\mathrm{\phi}$", "bins" : np.linspace(-1,1,nbins)},
  "zpr_PF_dz" :     {"name" : "Particle dz", "bins" : np.linspace(-100,100,nbins)},
  "zpr_PF_d0" :     {"name" : "Particle d0", "bins" : np.linspace(-100,100,nbins)},
  "zpr_PF_pdgId" :  {"name" : "Particle pdgid", "bins" : nbins},

  "zpr_SV_mass"     :  {"name" : "SV mass (GeV)", "bins" : np.linspace(0,180,nbins)},
  "zpr_SV_dlen"     :  {"name" : "SV decay length (cm)" , "bins" : np.linspace(0,250,nbins)},
  "zpr_SV_dlenSig"  :  {"name" : "SV decay length significance" , "bins" : np.linspace(0,6e3,nbins)},
  "zpr_SV_dxy"      :  {"name" : "SV 2D decay length (cm)" , "bins" : np.linspace(0,100,nbins)},
  "zpr_SV_dxySig"   :  {"name" : "SV 2D decay length significance" , "bins" : np.linspace(0,6e3,nbins)},
  "zpr_SV_chi2"     :  {"name" : "SV chi squared/ndof" , "bins" : np.linspace(-5e4,5e4,nbins)},
  "zpr_SV_ptrel"    :  {"name" : "SV relative $\mathrm{p_T}$" , "bins" : np.linspace(0,1,nbins)},
  "zpr_SV_x"        :  {"name" : "SV x position (cm)" , "bins" : np.linspace(-80,80,nbins)},
  "zpr_SV_y"        :  {"name" : "SV y position (cm)" , "bins" : np.linspace(-80,80,nbins)},
  "zpr_SV_z"        :  {"name" : "SV z position (cm)" , "bins" : np.linspace(-150,150,nbins)},
  "zpr_SV_pAngle"   :  {"name" : "SV pointing angle" , "bins" : np.linspace(0,3.5,nbins)},
  "zpr_SV_etarel"   :  {"name" : "SV relative $\mathrm{\eta}$", "bins" : np.linspace(-1,1,nbins)},
  "zpr_SV_phirel"   :  {"name" : "SV relative $\mathrm{\phi}$", "bins" : np.linspace(-1,1,nbins)},


}

_singleton_labels=["zpr_fj_msd","zpr_fj_pt","zpr_fj_eta","zpr_fj_phi","zpr_fj_n2b1","zpr_fj_tau21","zpr_fj_particleNetMD_QCD", "zpr_fj_particleNetMD_Xbb", "zpr_fj_particleNetMD_Xcc", "zpr_fj_particleNetMD_Xqq","zpr_fj_nBHadrons","zpr_fj_nCHadrons", "zpr_genAK8Jet_mass","zpr_genAK8Jet_pt","zpr_genAK8Jet_eta","zpr_genAK8Jet_phi", "zpr_genAK8Jet_partonFlavour","zpr_genAK8Jet_hadronFlavour", "zpr_fj_nBtags","zpr_fj_nCtags","zpr_fj_nLtags","zpr_fj_nparts"]
_singleton_features_labels=["zpr_fj_jetNSecondaryVertices","zpr_fj_jetNTracks","zpr_fj_tau1_trackEtaRel_0","zpr_fj_tau1_trackEtaRel_1","zpr_fj_tau1_trackEtaRel_2","zpr_fj_tau2_trackEtaRel_0","zpr_fj_tau2_trackEtaRel_1","zpr_fj_tau2_trackEtaRel_3","zpr_fj_tau1_flightDistance2dSig","zpr_fj_tau2_flightDistance2dSig","zpr_fj_tau1_vertexDeltaR","zpr_fj_tau1_vertexEnergyRatio","zpr_fj_tau2_vertexEnergyRatio","zpr_fj_tau1_vertexMass","zpr_fj_tau2_vertexMass","zpr_fj_trackSip2dSigAboveBottom_0","zpr_fj_trackSip2dSigAboveBottom_1","zpr_fj_trackSip2dSigAboveCharm","zpr_fj_trackSip3dSig_0","zpr_fj_trackSip3dSig_0","zpr_fj_tau1_trackSip3dSig_1","zpr_fj_trackSip3dSig_1","zpr_fj_tau2_trackSip3dSig_0","zpr_fj_tau2_trackSip3dSig_1","zpr_fj_trackSip3dSig_2","zpr_fj_trackSip3dSig_3","zpr_fj_z_ratio"]
_p_features_labels=["zpr_PF_ptrel","zpr_PF_etarel","zpr_PF_phirel","zpr_PF_dz","zpr_PF_d0","zpr_PF_pdgId"]
_SV_features_labels=["zpr_SV_mass","zpr_SV_dlen","zpr_SV_dlenSig","zpr_SV_dxy","zpr_SV_dxySig","zpr_SV_chi2","zpr_SV_ptrel","zpr_SV_x","zpr_SV_y","zpr_SV_z","zpr_SV_pAngle","zpr_SV_etarel","zpr_SV_phirel"]

def reshape_inputs(array, n_features):
    array = np.split(array, n_features, axis=-1)
    array = np.concatenate([np.expand_dims(array[i],axis=-1) for i in range(n_features)],axis=-1)
    return array

def train_val_test_split(array,train=0.8,val=0.1,test=0.1):
    n_events = array.shape[0]
    return array[:int(n_events*train)], array[int(n_events*train):int(n_events*(train+val))], array[int(n_events*(train+val)):int(n_events*(train+val+test))]

def axis_settings(ax):
    import matplotlib.ticker as plticker
    #ax.xaxis.set_major_locator(plticker.MultipleLocator(base=20))
    ax.xaxis.set_minor_locator(plticker.AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(plticker.AutoMinorLocator(5))
    ax.tick_params(direction='in', axis='both', which='major', labelsize=24, length=12)#, labelleft=False )
    ax.tick_params(direction='in', axis='both', which='minor' , length=6)
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')    
    #ax.grid(which='minor', alpha=0.5, axis='y', linestyle='dotted')
    ax.grid(which='major', alpha=0.9, linestyle='dotted')
    return ax

def makedir(outdir):
    if os.path.isdir(outdir):
        from datetime import datetime
        now = datetime.now()
        outdir += now.strftime("%Y_%D_%H_%M").replace("/","_")
    os.system("mkdir -p "+outdir )

    return outdir

def plot_features(array, labels, feature_labels, outdir, text_label=None):
    array = np.nan_to_num(array,nan=0.0, posinf=0., neginf=0.) 
    if labels.shape[1]==2: 
        processes = ["Z'","QCD"]
    else: 
        processes = ["Z'(bb)","Z'(cc)","Z'(qq)","QCD"]

    if len(array.shape) == 2:
        for ifeat in range(array.shape[-1]):
            plt.clf()
            fig,ax = plt.subplots() 
            hep.cms.label("Preliminary",rlabel=rlabel, data=False)
            ax = axis_settings(ax)
            for ilabel in range(labels.shape[1]):
               try: 
                   x_label = _titles[feature_labels[ifeat]]["name"]
                   bins    = _titles[feature_labels[ifeat]]["bins"]
               except:
                   x_label = feature_labels[ifeat]
                   bins    = 20

               tmp = array[labels[:,ilabel].astype(bool),ifeat]
               ax.hist(tmp,  
                       label=processes[ilabel], bins=bins, 
                       histtype='step',alpha=0.7, 
                       density=True,
               )
            ax.set_yscale('log')
            ax.set_xlabel(x_label,horizontalalignment='right',x=1.0,**axis_font)
            ax.set_ylabel("Normalized counts",horizontalalignment='right',y=1.0,**axis_font)
            ax.legend(loc="upper right",prop=legend_font)
            plt.tight_layout()
            plt.savefig(outdir+'/'+feature_labels[ifeat]+'.png')
            plt.savefig(outdir+'/'+feature_labels[ifeat]+'.pdf')
            plt.clf()
            if ifeat > 1:
                ibin=0
                for msd_lo,msd_hi in [(40.,80.),(80.,120.),(120.,160.),(160.,250.),(250.,350.)]:
                    fig,ax = plt.subplots()
                    hep.cms.label("Preliminary",rlabel=rlabel, data=False)
                    for ilabel in range(labels.shape[1]):
                        msd_idxs = (array[:,0] > msd_lo) & (array[:,0] < msd_hi) & (labels[:,ilabel]==1)
                        tmp = array[msd_idxs,ifeat]
                        ax.hist(tmp,
                                label=processes[ilabel], bins=bins,
                                histtype='step',alpha=0.7,
                                density=True,
                        )
                    ax.text(0.6,0.85,"%.0f < $\mathrm{m_{SD}}$ < %.0f"%(msd_lo,msd_hi),transform=ax.transAxes)
                    ax.set_yscale('log')
                    ax.set_xlabel(x_label,horizontalalignment='right',x=1.0,**axis_font)
                    ax.set_ylabel("Normalized counts",horizontalalignment='right',y=1.0,**axis_font)
                    ax.legend(loc="upper right",prop=legend_font)
                    plt.tight_layout()
                    plt.savefig(outdir+'/'+feature_labels[ifeat]+'_msdbin'+str(ibin)+'.png')
                    plt.savefig(outdir+'/'+feature_labels[ifeat]+'_msdbin'+str(ibin)+'.pdf')
                    ibin+=1
    elif len(array.shape) == 3:
        max_parts = 10
        for ifeat in range(array.shape[-1]):
            for ipart in range(array.shape[1]):
                plt.clf()
                fig,ax = plt.subplots() 
                ax = axis_settings(ax)
                for ilabel in range(labels.shape[1]):
                    tmp = array[labels[:,ilabel].astype(bool),ipart,ifeat]
                    try: 
                        x_label = _titles[feature_labels[ifeat]]["name"]
                        bins    = _titles[feature_labels[ifeat]]["bins"]
                    except:
                        x_label = feature_labels[ifeat]
                        bins    = 20
                    ax.hist(tmp,  
                        label=processes[ilabel], bins=bins, 
                        histtype='step',alpha=0.7, 
                        density=True,
                    )
                    ax.text(0.63,0.85,text_label+" "+str(ipart),transform=ax.transAxes,)
                    ax.set_yscale('log')
                    ax = axis_settings(ax)
                    ax.set_xlabel(x_label,horizontalalignment='right',x=1.0,**axis_font)
                    ax.set_ylabel("Normalized counts",horizontalalignment='right',y=1.0,**axis_font)
                    ax.legend(loc="upper right",prop=legend_font)
                    hep.cms.label("Preliminary",rlabel=rlabel, data=False)
                    plt.tight_layout()
                    plt.savefig(outdir+'/'+'ipart_'+str(ipart)+'_'+feature_labels[ifeat]+'.png')
                    plt.savefig(outdir+'/'+'ipart_'+str(ipart)+'_'+feature_labels[ifeat]+'.pdf')
                if ipart > 10: break
    else:
        raise ValueError("I don't understand this array shape",array.shape)

def plot_loss(loss_vals_training,loss_vals_validation,opath):
    plt.clf()
    fig,ax = plt.subplots()
    hep.cms.label("Preliminary",rlabel=rlabel, data=False)
    ax = axis_settings(ax)
 
    loss_vals_training = loss_vals_training[loss_vals_training!=0]
    loss_vals_validation = loss_vals_validation[loss_vals_validation!=0]

    ax.plot(range(1,len(loss_vals_training)+1), loss_vals_training, lw=2.0,label="training") 
    ax.plot(range(1,len(loss_vals_validation)+1), loss_vals_validation, lw=2.0, label="validation") 
    ax.set_xlabel("Epoch",horizontalalignment='right',x=1.0,**axis_font)
    ax.set_ylabel("Loss",horizontalalignment='right',y=1.0,**axis_font)
    ax.legend(loc="upper right",prop=legend_font)
    plt.tight_layout()
    plt.savefig(opath+"/loss.png")

def plot_response(testLabels, testPredictions, training_text, opath, modelName, nn_bins,ilabel,all_vs_QCD=False, plot=False):
    if testLabels.shape[1]==2: 
        processes = ["Z\'","QCD"]
    elif testLabels.shape[1]==3: 
        processes = ["Z'(bb) vs QCD","Z'(cc) vs QCD","Z'(qq) vs QCD"]
    else: 
        processes = ["Z\'(bb)","Z\'(cc)","Z\'(qq)","QCD"]
    plt.clf()
    fig,ax = plt.subplots()
    hep.cms.label("Preliminary",rlabel=rlabel, data=False)
    ax = axis_settings(ax)
    response_l = [] 
    #bins=None

    for itruth in range(testLabels.shape[1]):
        response, bins, _ = plt.hist(testPredictions[testLabels[:,itruth]>0,ilabel],
            bins=nn_bins,
            label=processes[itruth],
            histtype='step',alpha=0.7,
            #density=True,
            lw=2.0,
        )
        response /= np.sum(response)
        response_l.append(response)
  
    if all_vs_QCD:
        qcd_idxs = np.where(testLabels.sum(axis=1)==0,True,False)
        response, bins, _ = plt.hist(testPredictions[qcd_idxs,ilabel],
            bins=nn_bins,
            label=processes[-1],
            histtype='step',alpha=0.7,
            #density=True,
            lw=2.0,
        ) 
        response /= np.sum(response)
        response_l.append(response)
 
    if plot:
        ax.text(0.60,0.85,"\n".join(training_text),transform=ax.transAxes,**inlay_font)
        ax.set_yscale('log')
        ax = axis_settings(ax)
        ax.set_xlabel(processes[ilabel] + " output",horizontalalignment='right',x=1.0,**axis_font)
        ax.set_xlim(-0.01,1.01)
        ax.set_ylabel("Normalized counts",horizontalalignment='right',y=1.0,**axis_font)
        ax.legend(loc="upper right",prop=legend_font)
        plt.tight_layout()
        plt.savefig(opath+"/%s_response_class_%s.png"%(modelName,ilabel))
        plt.savefig(opath+"/%s_response_class_%s.pdf"%(modelName,ilabel))
        return 

    print(response_l, bins)
    return response_l, bins
def plot_roc_curve(testLabels, testPredictions, training_text, opath, modelName, all_vs_QCD, QCD_only):
    os.system("mkdir -p "+opath)
    if testLabels.shape[1]==2:
        processes = ["Z'","QCD"]
    elif testLabels.shape[1]==3: 
        processes = ["Z'(bb) vs QCD","Z'(cc) vs QCD","Z'(qq) vs QCD"]
    else:
        processes = ["Z'(bb)","Z'(cc)","Z'(qq)","QCD"]
    training_text = training_text.split(":")

        
    n_processes = testLabels.shape[1]
    #if all_vs_QCD:
    #    n_processes -= 1 
    #for ilabel in range(testLabels.shape[1]):
    for ilabel in range(n_processes):
        nn_bins = np.linspace(-0.001,1.001,1000) 
        #nn_bins = np.concatenate((np.linspace(0.,0.0039,10000) , np.linspace(0.004,0.993,1000), np.linspace(0.994,1.0001,10000)))
        #nn_bins = np.concatenate((np.linspace(-0.001,0.04,10000) , np.linspace(0.041,0.95,10000), np.linspace(0.95001,1.001,10000)))
        plot_response(testLabels, testPredictions, training_text, opath, modelName, np.linspace(-0.01,1.01,50), ilabel, all_vs_QCD=all_vs_QCD, plot=True)
        response_l, bins = plot_response(testLabels, testPredictions, training_text, opath, modelName, nn_bins, ilabel, all_vs_QCD=all_vs_QCD, plot=False)
        tpr = None
        fpr_l = []
        fpr_label_l = []
        for itruth in range(testLabels.shape[1]):
            #>>> bins = np.concatenate((np.linspace(0.00,0.004,10000), np.linspace(0.004,0.994, 1000), np.linspace(0.994,1.0, 10000)))
            #>>> [np.sum(output[ib:]) for ib in range(len(bins),0,-1)]
            print ([np.sum(response_l[itruth][ib:]) for ib in range(len(nn_bins),0,-1) ])
            print(np.sum(response_l[itruth]))
            #if QCD_only and "QCD" not in processes[itruth]: continue 
            if itruth == ilabel:
                tpr = [ np.sum(response_l[itruth][ib:])/np.sum(response_l[itruth]) for ib in range(len(nn_bins),0,-1) ]
            else:
 
                fpr_l.append([ np.sum(response_l[itruth][ib:])/np.sum(response_l[itruth]) for ib in range(len(nn_bins),0,-1) ])
                fpr_label_l.append(processes[itruth])
            #print(processes[itruth], response_l, bins)
        print(tpr,fpr_l)
        if all_vs_QCD:
            fpr_l.append([ np.sum(response_l[-1][ib:])/np.sum(response_l[-1]) for ib in range(len(nn_bins),0,-1) ])
            fpr_label_l.append("QCD")

        plt.clf()
        fig,ax = plt.subplots()
        hep.cms.label("Preliminary",rlabel=rlabel, data=False)
        ax = axis_settings(ax)
        for i in range(len(fpr_l)):
            fpr = np.round_(fpr_l[i],decimals=4)
            tpr = np.round_(tpr,decimals=4)
            if QCD_only and "QCD" not in fpr_label_l[i]: continue
            ax.plot(fpr_l[i], tpr, 
                    label = "{process} vs {class_name} (auc={auc:.2f})".format(process=fpr_label_l[i],class_name=processes[ilabel],auc=auc(fpr, tpr)),
                    lw=2.0,
                   )
            if "QCD" in fpr_label_l[i]:
                np.savez(opath+'/'+processes[ilabel]+'_vsQCD.npz',tpr=tpr,fpr=fpr_l[i])
        ax.set_xlabel("False positive rate",horizontalalignment='right',x=1.0,**axis_font)
        ax.set_xlim(0.,1.0)
        ax.set_ylabel("True positive rate",horizontalalignment='right',y=1.0,**axis_font)
        ax.set_ylim(0.,1.0)
        ax.axvline(x=0.05,ls='--',lw=1.0,c='magenta')
        ax.text(0.63,0.2,"\n".join(training_text),transform=ax.transAxes,**inlay_font)
        ax.legend(loc="lower right",prop=legend_font)
        plt.tight_layout()
        plt.savefig(opath+"/%s_roc_class_%s%s.png"%(modelName,ilabel,"QCD-only" if QCD_only else ""))
        plt.savefig(opath+"/%s_roc_class_%s%s.pdf"%(modelName,ilabel,"QCD-only" if QCD_only else "" ))

        ax.set_xlim(0.001,1.0)
        ax.set_ylim(0.001,1.0) 
        ax.set_xscale('log')
        ax.set_yscale('log')
        plt.savefig(opath+"/%s_roc_class_%s_log%s.png"%(modelName,ilabel,"QCD-only" if QCD_only else ""))
        plt.savefig(opath+"/%s_roc_class_%s_log%s.pdf"%(modelName,ilabel,"QCD-only" if QCD_only else "" ))

    return 

def plot_correlation(x,y,x_name,y_name,x_bins,y_bins,opath,name):
    plt.clf()
    fig,ax = plt.subplots()
    hep.cms.label("Preliminary",rlabel=rlabel, data=False)
    ax = axis_settings(ax)
    #ax.scatter(x,y,s=0.1,c="black")
    ax.hist2d(x,y,bins=(x_bins,y_bins),norm=matplotlib.colors.LogNorm(), cmap=matplotlib.cm.viridis)
    ax.set_xlabel(x_name, horizontalalignment='right',x=1.0,**axis_font)
    ax.set_ylabel(y_name, horizontalalignment='right',y=1.0,**axis_font)
 

    #from mpl_toolkits.axes_grid1 import make_axes_locatable
    #divider = make_axes_locatable(ax)
    #cax = divider.append_axes('right', size='5%', pad=0.05)
    #im = ax.imshow(data, cmap='bone')
    #fig.colorbar(im, cax=cax, orientation='vertical')

    plt.tight_layout()
    plt.savefig(opath+"/2dcorr_%s.png"%(name))
    plt.savefig(opath+"/2dcorr_%s.pdf"%(name))
    
def sculpting_curves(testQcdPredictions, testQcdKinematics, training_text, opath, modelName, inverted=False,score=""):

    ##This isn't enough bins???
    bins = np.linspace(-0.001,1.001,10000)
    #bins = np.concatenate((np.linspace(-0.001,0.0004,10000),np.linspace(0.0004,1.00,10000)))
    QcdPredictionsPdf,edges = np.histogram(testQcdPredictions, bins=bins, density=True)

    #tot = 0
    #QcdPredictionsCdf = [] 
    #for i,ih in enumerate(QcdPredictionsPdf):
    #    current = ih*(edges[i+1]-edges[i])
    #    tot += current
    #    QcdPredictionsCdf.append(tot)

    pctls = [0.05,0.10,0.25,0.75,1.00]
    print("before",QcdPredictionsPdf)
    #if testQcdPredictions.mean()<0.5:
    if inverted:
        #QcdPredictionsPdf = QcdPredictionsPdf[::-1]
        invert=True
        #pctls = [
        pctls = [1-pctl for pctl in pctls]
    print("after",QcdPredictionsPdf)
    QcdPredictionsCdf = np.cumsum(QcdPredictionsPdf)*(edges[1]-edges[0])
    cuts = np.searchsorted(QcdPredictionsCdf,pctls)

    

    sculpting_vars = ["zpr_fj_msd","zpr_fj_pt","zpr_fj_eta","zpr_fj_phi","zpr_genAK8Jet_mass","zpr_genAK8Jet_pt","zpr_genAK8Jet_eta","zpr_genAK8Jet_phi", "zpr_genAK8Jet_partonFlavour","zpr_genAK8Jet_hadronFlavour","zpr_fj_nparts","zpr_fj_nBHadrons","zpr_fj_nCHadrons",]
    training_text = training_text.split(":")
    if score:
        training_text.append(score + " score")



    plt.clf()
    fig,ax=plt.subplots()
    hep.cms.label("Preliminary",rlabel=rlabel, data=False)
    ax = axis_settings(ax)
    for c,p in zip(cuts,pctls):
        ax.hist(testQcdPredictions[testQcdPredictions<edges[c]] if not inverted else testQcdPredictions[testQcdPredictions>edges[c]],
                label="$\mathrm{\epsilon_{QCD}}=$%.2f"%(p if not inverted else 1-p),
                bins=bins,
                histtype='step',
                alpha=0.7,
                density=True,
                lw=2.0,
        )
    ax.set_xlabel("Tagger score",horizontalalignment='right',x=1.0,**axis_font)
    ax.set_ylabel("Normalized counts",horizontalalignment='right',y=1.0,**axis_font)
    ax.text(0.56,0.82,"\n".join(training_text),transform=ax.transAxes,**inlay_font)
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(opath+"/%s_scores_after_cuts_%s.png"%(modelName,"_"+score if score else ""))
    plt.savefig(opath+"/%s_scores_after_cuts_%s.pdf"%(modelName,"_"+score if score else ""))

    for i,label in enumerate(sculpting_vars): 
        plt.clf()
        fig,ax=plt.subplots()
        hep.cms.label("Preliminary",rlabel=rlabel, data=False)
        ax = axis_settings(ax)


        inclusive_hist,_ = np.histogram(testQcdKinematics[:,_singleton_labels.index(label)], bins=_titles[label]["bins"],)

        for c,p in zip(cuts,pctls):
            #print("QCD < %.2f"%edges[c], testQcdPredictions[testQcdPredictions<edges[c]])
            KinematicsPassingCut = testQcdKinematics[testQcdPredictions<edges[c],_singleton_labels.index(label)] if not inverted else testQcdKinematics[testQcdPredictions>edges[c],_singleton_labels.index(label)]
            cut_hist,_ = np.histogram(KinematicsPassingCut,bins=_titles[label]["bins"],)
            jsd = scipy.spatial.distance.jensenshannon(inclusive_hist,cut_hist)
            ax.hist(KinematicsPassingCut, 
                    label="$\mathrm{\epsilon_{QCD}}=$%.2f, %.2f"%((p if not inverted else 1-p),0. if jsd == np.nan else jsd), 
                    bins=_titles[label]["bins"],
                    histtype='step',
                    alpha=0.7,
                    density=True,
                    lw=2.0,
                    )
        ax.set_xlabel(_titles[label]["name"],horizontalalignment='right',x=1.0,**axis_font)
        ax.set_ylabel("Normalized counts",horizontalalignment='right',y=1.0,**axis_font)
        ax.text(0.56,0.82,"\n".join(training_text),transform=ax.transAxes,**inlay_font)
        ax.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(opath+"/%s_sculpting_qcd_var%i%s.png"%(modelName,i,"_"+score if score else ""))
        plt.savefig(opath+"/%s_sculpting_qcd_var%i%s.pdf"%(modelName,i,"_"+score if score else ""))
        ax.set_yscale('log')
        ax = axis_settings(ax)
        plt.savefig(opath+"/%s_sculpting_qcd_var%i_log%s.png"%(modelName,i,"_"+score if score else ""))
        plt.savefig(opath+"/%s_sculpting_qcd_var%i_log%s.pdf"%(modelName,i,"_"+score if score else ""))
