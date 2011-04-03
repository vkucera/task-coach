//
//  TaskHeaderView.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface TaskHeaderView : UIView
{
    IBOutlet UIImageView *imageView;
    IBOutlet UILabel *textLabel;
    UIImage *bgImage;
}

- (void)setStyle:(NSInteger)style; // TASKSTATUS constants

@end
