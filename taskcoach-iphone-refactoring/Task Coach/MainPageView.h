//
//  MainPageView.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 12/03/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "ImageButton.h"

@interface MainPageView : UIViewController
{
    IBOutlet ImageButton *todayButton;
    IBOutlet ImageButton *configureButton;
    IBOutlet ImageButton *listsButton;
    IBOutlet UILabel *listsLabel;
    IBOutlet ImageButton *syncButton;
}

- (id)init;

@end
