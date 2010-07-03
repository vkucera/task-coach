//
//  PaperHeaderView.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 27/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface PaperHeaderView : UIView
{
	UIImage *bgImage;
	UILabel *label;
}

@property (nonatomic, retain) IBOutlet UILabel *label;

@end
