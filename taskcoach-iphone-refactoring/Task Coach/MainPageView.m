//
//  MainPageView.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 12/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "MainPageView.h"
#import "CDList.h"
#import "Configuration.h"
#import "TasklistView.h"
#import "i18n.h"

@implementation MainPageView

- (id)init
{
    if ((self = [super initWithNibName:@"MainPageView-iPhone" bundle:[NSBundle mainBundle]]))
    {
    }

    return self;
}

- (void)dealloc
{
    [todayButton release];
    [configureButton release];
    [listsButton release];
    [listsLabel release];
    [syncButton release];
    [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];

    [todayButton setTarget:self action:@selector(doShowToday:)];
    [listsButton setTarget:self action:@selector(doShowLists:)];
    [configureButton setTarget:self action:@selector(doConfigure:)];
    [syncButton setTarget:self action:@selector(doSync:)];
}

- (void)viewDidUnload
{
    [todayButton release];
    todayButton = nil;
    [configureButton release];
    configureButton = nil;
    [listsButton release];
    listsButton = nil;
    [listsLabel release];
    listsLabel = nil;
    [syncButton release];
    syncButton = nil;
    [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated
{
    CDList *list = [Configuration instance].currentList;
    if (list)
        listsLabel.text = list.name;
    else
        listsLabel.text = _("Lists");
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return NO;
}

#pragma mark - Actions

- (void)doShowToday:(id)sender
{
}

- (void)doConfigure:(id)sender
{
}

- (void)doShowLists:(id)sender
{
    if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPhone)
    {
        TasklistView *ctrl = [[TasklistView alloc] initWithTarget:self action:@selector(onSave:)];
        ctrl.view.frame = self.view.frame;
        ctrl.view.hidden = YES;
        [self.view.superview addSubview:ctrl.view];

        [UIView transitionWithView:self.view.superview
                          duration:1
                           options:UIViewAnimationOptionTransitionFlipFromRight
         | UIViewAnimationOptionAllowAnimatedContent
                        animations:^(void)
        {
            self.view.hidden = YES;
            ctrl.view.hidden = NO;
        }
                        completion:NULL];
    }
    else
    {
        // XXXTODO
    }
}

- (void)doSync:(id)sender
{
}

- (void)onSave:(UIViewController *)ctrl
{
    [UIView transitionWithView:self.view.superview
                      duration:1.0
                       options:UIViewAnimationOptionTransitionFlipFromLeft
                    animations:^(void)
    {
        [self viewWillAppear:YES];
        self.view.hidden = NO;
        ctrl.view.hidden = YES;
    }
                    completion:^(BOOL finished)
    {
        [ctrl.view removeFromSuperview];
        [ctrl release];
    }];
}

@end
